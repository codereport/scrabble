#!/usr/bin/env python3
"""
Generate an HTML page showing words with exactly one hook, organized by prefix/suffix and letter.
"""

from collections import defaultdict

def load_dictionary(filepath):
    """Load words from dictionary file, extracting just the word part."""
    words = set()
    with open(filepath, 'r') as f:
        for line in f:
            # Extract the word (everything before the first space)
            word = line.split()[0] if line.strip() else None
            if word:
                words.add(word.upper())
    return words

def find_one_hook_words(dictionary_path):
    """Find words that have exactly one prefix hook OR exactly one suffix hook.
    Prefix and suffix hooks are counted separately."""
    words = load_dictionary(dictionary_path)
    results = []
    
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    for word in sorted(words):
        # Find valid prefixes
        prefix_hooks = []
        for letter in alphabet:
            candidate = letter + word
            if candidate in words and candidate != word:
                prefix_hooks.append(letter)
        
        # Find valid suffixes (excluding 's')
        suffix_hooks = []
        for letter in alphabet:
            if letter == 'S':  # Ignore 's' suffix
                continue
            candidate = word + letter
            if candidate in words and candidate != word:
                suffix_hooks.append(letter)
        
        # Add to results if exactly one prefix hook
        if len(prefix_hooks) == 1:
            results.append({
                'word': word,
                'hook_type': 'prefix',
                'hook_letter': prefix_hooks[0],
                'result_word': prefix_hooks[0] + word
            })
        
        # Add to results if exactly one suffix hook (independent of prefix)
        if len(suffix_hooks) == 1:
            results.append({
                'word': word,
                'hook_type': 'suffix',
                'hook_letter': suffix_hooks[0],
                'result_word': word + suffix_hooks[0]
            })
    
    return results

def remove_plural_duplicates(results, all_words):
    """Remove words that are just plurals of other words in the results.
    Also remove base words if their S-plural exists in the dictionary."""
    # Create a set of all words in results
    result_words = {r['word'] for r in results}
    
    filtered_results = []
    for r in results:
        word = r['word']
        
        # Case 1: If word ends in 'S' and the non-S version is also in results, skip the plural
        if word.endswith('S') and len(word) > 1:
            base_word = word[:-1]
            if base_word in result_words:
                continue  # Skip this plural
        
        # Case 2: If word + 'S' exists in dictionary AND is in results, skip the base word
        # This handles cases like JOT (which has hook A→JOTA) where JOTS also exists
        plural_word = word + 'S'
        if plural_word in all_words and plural_word in result_words:
            continue  # Skip the base word if its plural is also in results
        
        # Case 3: If word + 'S' exists in dictionary (even if not in results), 
        # filter it out to avoid plural duplicates
        # E.g., JOT has hook A→JOTA, but JOTS exists, so skip JOT
        if plural_word in all_words:
            continue
        
        filtered_results.append(r)
    
    return filtered_results

def generate_html(results, output_path):
    """Generate an HTML page organizing words by hook type and letter."""
    
    # Group results by hook type and letter
    prefix_by_letter = defaultdict(list)
    suffix_by_letter = defaultdict(list)
    
    for r in results:
        if r['hook_type'] == 'prefix':
            prefix_by_letter[r['hook_letter']].append(r)
        else:
            suffix_by_letter[r['hook_letter']].append(r)
    
    # Sort words within each letter group by length, then alphabetically
    for letter in prefix_by_letter:
        prefix_by_letter[letter].sort(key=lambda r: (len(r['word']), r['word']))
    for letter in suffix_by_letter:
        suffix_by_letter[letter].sort(key=lambda r: (len(r['word']), r['word']))
    
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>One-Hook Words - NWL 2020</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .stat-box {{
            background: rgba(255,255,255,0.2);
            padding: 15px 30px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .hook-type-nav {{
            background: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 2px solid #e9ecef;
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .hook-type-btn {{
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
            padding: 12px 30px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .hook-type-btn:hover {{
            background: #f0f2ff;
        }}
        
        .hook-type-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .letter-nav {{
            background: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 2px solid #e9ecef;
            display: flex;
            gap: 8px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .letter-btn {{
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
            padding: 8px 14px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            min-width: 40px;
        }}
        
        .letter-btn:hover {{
            background: #f0f2ff;
        }}
        
        .letter-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .letter-btn.disabled {{
            opacity: 0.3;
            cursor: not-allowed;
            border-color: #ccc;
            color: #ccc;
        }}
        
        .letter-btn.disabled:hover {{
            background: white;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            display: none;
        }}
        
        .section.active {{
            display: block;
        }}
        
        .letter-section {{
            display: none;
            animation: fadeIn 0.3s;
        }}
        
        .letter-section.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .letter-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            font-size: 1.5rem;
            font-weight: 700;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .letter-count {{
            font-size: 1rem;
            opacity: 0.9;
        }}
        
        .words-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 0 0 10px 10px;
        }}
        
        .word-item {{
            background: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .word-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        .word-base {{
            font-weight: 600;
            color: #333;
            font-size: 1.1rem;
        }}
        
        .word-hook {{
            color: #667eea;
            font-weight: 700;
        }}
        
        .word-result {{
            color: #666;
            font-size: 0.9rem;
            margin-left: 8px;
        }}
        
        .word-length {{
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            color: #666;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}
        
        .empty-state-icon {{
            font-size: 3rem;
            margin-bottom: 20px;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8rem;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .words-grid {{
                grid-template-columns: 1fr;
            }}
            
            .letter-nav, .hook-type-nav {{
                padding: 15px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 One-Hook Words</h1>
            <p>Words from NWL 2020 that can only be prefixed or suffixed by exactly one letter</p>
            <p style="font-size: 0.9rem; margin-top: 10px; opacity: 0.8;">(Ignoring 's' suffix and plural duplicates)</p>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{len(results):,}</div>
                    <div class="stat-label">Total Words</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len([r for r in results if r['hook_type'] == 'prefix']):,}</div>
                    <div class="stat-label">Prefix Hooks</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len([r for r in results if r['hook_type'] == 'suffix']):,}</div>
                    <div class="stat-label">Suffix Hooks</div>
                </div>
            </div>
        </header>
        
        <div class="hook-type-nav">
            <button class="hook-type-btn active" onclick="showHookType('prefix')">📍 Prefix Hooks</button>
            <button class="hook-type-btn" onclick="showHookType('suffix')">📌 Suffix Hooks</button>
        </div>
        
        <div class="letter-nav" id="letter-nav">
"""
    
    # Add letter buttons
    for letter in alphabet:
        has_prefix = letter in prefix_by_letter
        has_suffix = letter in suffix_by_letter
        html += f'            <button class="letter-btn" data-letter="{letter}" onclick="showLetter(\'{letter}\')">{letter}</button>\n'
    
    html += """        </div>
        
        <div class="content">
            <!-- PREFIX HOOKS SECTION -->
            <div class="section active" id="prefix-section">
"""
    
    # Add prefix hooks by letter
    first_prefix_letter = None
    for letter in alphabet:
        if letter in prefix_by_letter:
            if first_prefix_letter is None:
                first_prefix_letter = letter
            words_list = prefix_by_letter[letter]
            active_class = ' active' if letter == first_prefix_letter else ''
            html += f"""
                <div class="letter-section prefix-letter-{letter}{active_class}" data-letter="{letter}">
                    <div class="letter-header">
                        <span>Letter {letter}</span>
                        <span class="letter-count">{len(words_list)} words</span>
                    </div>
                    <div class="words-grid">
"""
            for r in words_list:
                html += f"""
                        <div class="word-item">
                            <div>
                                <span class="word-hook">{r['hook_letter']}</span><span class="word-base">{r['word']}</span>
                                <span class="word-result">→ {r['result_word']}</span>
                            </div>
                            <span class="word-length">len {len(r['word'])}</span>
                        </div>
"""
            html += """
                    </div>
                </div>
"""
    
    html += """
            </div>
            
            <!-- SUFFIX HOOKS SECTION -->
            <div class="section" id="suffix-section">
"""
    
    # Add suffix hooks by letter
    first_suffix_letter = None
    for letter in alphabet:
        if letter in suffix_by_letter:
            if first_suffix_letter is None:
                first_suffix_letter = letter
            words_list = suffix_by_letter[letter]
            active_class = ' active' if letter == first_suffix_letter else ''
            html += f"""
                <div class="letter-section suffix-letter-{letter}{active_class}" data-letter="{letter}">
                    <div class="letter-header">
                        <span>Letter {letter}</span>
                        <span class="letter-count">{len(words_list)} words</span>
                    </div>
                    <div class="words-grid">
"""
            for r in words_list:
                html += f"""
                        <div class="word-item">
                            <div>
                                <span class="word-base">{r['word']}</span><span class="word-hook">{r['hook_letter']}</span>
                                <span class="word-result">→ {r['result_word']}</span>
                            </div>
                            <span class="word-length">len {len(r['word'])}</span>
                        </div>
"""
            html += """
                    </div>
                </div>
"""
    
    # Build JavaScript data for available letters
    prefix_letters = list(prefix_by_letter.keys())
    suffix_letters = list(suffix_by_letter.keys())
    
    html += f"""
            </div>
        </div>
    </div>
    
    <script>
        let currentHookType = 'prefix';
        const prefixLetters = {prefix_letters};
        const suffixLetters = {suffix_letters};
        
        function showHookType(type) {{
            currentHookType = type;
            
            // Update hook type buttons
            document.querySelectorAll('.hook-type-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            // Show/hide sections
            document.querySelectorAll('.section').forEach(section => {{
                section.classList.remove('active');
            }});
            document.getElementById(type + '-section').classList.add('active');
            
            // Update letter buttons
            updateLetterButtons();
            
            // Show first available letter for this type
            const availableLetters = type === 'prefix' ? prefixLetters : suffixLetters;
            if (availableLetters.length > 0) {{
                showLetter(availableLetters[0]);
            }}
        }}
        
        function updateLetterButtons() {{
            const availableLetters = currentHookType === 'prefix' ? prefixLetters : suffixLetters;
            document.querySelectorAll('.letter-btn').forEach(btn => {{
                const letter = btn.getAttribute('data-letter');
                if (availableLetters.includes(letter)) {{
                    btn.classList.remove('disabled');
                }} else {{
                    btn.classList.add('disabled');
                    btn.classList.remove('active');
                }}
            }});
        }}
        
        function showLetter(letter) {{
            const availableLetters = currentHookType === 'prefix' ? prefixLetters : suffixLetters;
            
            // Don't allow selecting unavailable letters
            if (!availableLetters.includes(letter)) {{
                return;
            }}
            
            // Update letter buttons
            document.querySelectorAll('.letter-btn').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.getAttribute('data-letter') === letter) {{
                    btn.classList.add('active');
                }}
            }});
            
            // Show/hide letter sections
            const sectionPrefix = currentHookType === 'prefix' ? 'prefix-letter-' : 'suffix-letter-';
            document.querySelectorAll('.letter-section').forEach(section => {{
                section.classList.remove('active');
            }});
            
            const targetSection = document.querySelector('.' + sectionPrefix + letter);
            if (targetSection) {{
                targetSection.classList.add('active');
            }}
        }}
        
        // Initialize on page load
        updateLetterButtons();
    </script>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html)

def main():
    dictionary_path = '/home/cph/scrabble/scrabble/dictionary/nwl_2020.txt'
    
    print("Loading dictionary and finding one-hook words...")
    all_words = load_dictionary(dictionary_path)
    results = find_one_hook_words(dictionary_path)
    
    print(f"Found {len(results)} words with exactly one hook")
    
    # Remove plural duplicates
    results = remove_plural_duplicates(results, all_words)
    print(f"After removing plural duplicates: {len(results)} words")
    
    # Sort by word length (shortest first), then alphabetically
    results.sort(key=lambda r: (len(r['word']), r['word']))
    
    # Generate HTML
    output_path = '/home/cph/scrabble/scrabble/dictionary/one_hook_words.html'
    print(f"\nGenerating HTML page...")
    generate_html(results, output_path)
    
    print(f"✓ HTML page created: {output_path}")
    print(f"\nStatistics:")
    print(f"  Total words: {len(results)}")
    print(f"  Prefix hooks: {len([r for r in results if r['hook_type'] == 'prefix'])}")
    print(f"  Suffix hooks: {len([r for r in results if r['hook_type'] == 'suffix'])}")

if __name__ == '__main__':
    main()

