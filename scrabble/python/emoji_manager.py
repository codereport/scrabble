
import os
from PIL import Image, ImageDraw, ImageFont
from sentence_transformers import SentenceTransformer, util
import emoji
import numpy as np
from pathlib import Path

# Path to Noto Color Emoji font
FONT_PATH = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
CACHE_DIR = Path(__file__).parent.parent / "emojis" / "generated"

class EmojiManager:
    def __init__(self):
        self.model = None
        self.emoji_embeddings = None
        self.emoji_list = None
        self.font_path = FONT_PATH
        
        # Ensure cache directory exists
        if not CACHE_DIR.exists():
            CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _load_model(self):
        if self.model is None:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self._initialize_emoji_database()

    def _initialize_emoji_database(self):
        # Create a curated list of emojis with descriptions
        # We can extract this from the emoji package or use a predefined list
        self.emoji_map = {}
        descriptions = []
        chars = []
        
        # Iterate over emojis to build a searchable database
        for char, data in emoji.EMOJI_DATA.items():
            if 'en' in data:
                name = data['en'].strip(':').replace('_', ' ')
                descriptions.append(name)
                chars.append(char)

        self.emoji_list = chars
        self.emoji_descriptions = descriptions
        
        # Pre-compute embeddings for emoji descriptions
        self.emoji_embeddings = self.model.encode(descriptions, convert_to_tensor=True)

    def get_emoji_for_definition(self, word: str, definition: str) -> str:
        self._load_model()
        
        # 1. Try exact keyword match in emoji name
        # Normalize word
        norm_word = word.lower().strip()
        
        # Simple heuristic: if word is in emoji name
        for char, name in zip(self.emoji_list, self.emoji_descriptions):
            if norm_word == name.lower():
                return char
            # Check for "word " or " word" to avoid partial matches like "tax" in "taxi"
            # But "taxi" in "oncoming taxi" is good.
            if f" {norm_word} " in f" {name.lower()} ":
                 # We prefer exact match, but this is a good candidate. 
                 # Let's collect candidates? No, keep it simple for now.
                 pass

        # Combine word and definition for better context
        query = f"emoji of {word}: {definition}"
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # Find closest match
        hits = util.semantic_search(query_embedding, self.emoji_embeddings, top_k=1)
        
        if hits and hits[0]:
            score = hits[0][0]['score']
            best_idx = hits[0][0]['corpus_id']
            emoji_char = self.emoji_list[best_idx]
            description = self.emoji_descriptions[best_idx]
            
            print(f"Emoji Search: '{word}' -> {emoji_char} ({description}) | Score: {score:.4f}")
            
            if score >= 0.39:
                return emoji_char
            else:
                print(f"Score too low (< 0.39), skipping emoji.")
                return None
        
        return None # Fallback

    def generate_emoji_image(self, emoji_char: str, size: int = 512) -> str:
        """
        Generates a PNG for the given emoji and returns the file path.
        Returns cached path if it already exists.
        Default size increased to 512 for better quality at large scales.
        """
        # Hex encode emoji for filename to avoid filesystem issues
        filename = "-".join(f"{ord(c):x}" for c in emoji_char) + f"_s{size}.png"
        
        filepath = CACHE_DIR / filename
        
        if filepath.exists():
            return str(filepath)
            
        try:
            # Create image with transparent background
            image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Load font
            # Note: 'sbix' table support (color bitmaps) in Pillow requires libraqm, 
            # and NotoColorEmoji uses CBDT/CBLC or COLR/CPAL which generic Pillow might handle as monochrome 
            # or might need specific versions. 
            # For standard Linux with NotoColorEmoji, it's often a bitmap font embedded.
            # Using 'mode="L"' or similar for mask if it fails to render color.
            # However, modern Pillow + proper freetype should handle it or at least render the outline.
            # Let's try standard loading.
            
            try:
                # Try loading NotoColorEmoji at fixed size 109 (common for bitmap fonts)
                # We need a larger canvas for this
                font_size = 109
                canvas_size = 128
                
                # If requested size is larger than bitmap source, we can't do much with bitmap fonts
                # BUT if we have a vector font fallback (like DejaVu), we should scale that up.
                # For NotoColorEmoji (bitmap), we might just have to live with it or upscale.
                # Let's try to generate at requested size if possible, or max available bitmap size.
                
                try:
                    font = ImageFont.truetype(self.font_path, font_size)
                except OSError:
                    try:
                        font = ImageFont.truetype("NotoColorEmoji.ttf", font_size)
                    except OSError:
                         raise OSError("Noto font not found")

                # If we succeeded with Noto, use the large canvas
                temp_image = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_image)
                
                # Center text
                try:
                    left, top, right, bottom = font.getbbox(emoji_char)
                    w = right - left
                    h = bottom - top
                except AttributeError:
                     w, h = temp_draw.textsize(emoji_char, font=font)
                
                x = (canvas_size - w) / 2
                y = (canvas_size - h) / 2
                
                temp_draw.text((x, y), emoji_char, font=font, embedded_color=True)
                
                # Resize to requested size
                image = temp_image.resize((size, size), resample=Image.Resampling.LANCZOS)
                
            except OSError:
                # Fallback to DejaVu Sans or other system font
                fallback_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                print(f"Falling back to {fallback_font}")
                try:
                     font = ImageFont.truetype(fallback_font, int(size * 0.9))
                except OSError:
                     print("Could not load fallback font.")
                     return None

                # Center text
                try:
                    left, top, right, bottom = font.getbbox(emoji_char)
                    w = right - left
                    h = bottom - top
                except AttributeError:
                     w, h = draw.textsize(emoji_char, font=font)
                
                x = (size - w) / 2
                y = (size - h) / 2
                
                draw.text((x, y), emoji_char, font=font, embedded_color=True)

            image.save(filepath)
            return str(filepath)
            
        except Exception as e:
            print(f"Error generating emoji image: {e}")
            return None

# Singleton instance
emoji_manager = EmojiManager()

