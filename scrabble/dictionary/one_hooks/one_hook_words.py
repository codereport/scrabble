#!/usr/bin/env python3
"""
Find words from NWL 2020 that can only be prefixed or suffixed by exactly one letter.
Ignores the suffix 's' when checking.
"""

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

def main():
    dictionary_path = '/home/cph/scrabble/scrabble/dictionary/nwl_2020.txt'
    all_words = load_dictionary(dictionary_path)
    results = find_one_hook_words(dictionary_path)
    
    print(f"Found {len(results)} words with exactly one hook (ignoring 's' suffix)")
    
    # Remove plural duplicates
    results = remove_plural_duplicates(results, all_words)
    print(f"After removing plural duplicates: {len(results)} words\n")
    
    # Sort by word length (shortest first), then alphabetically
    results.sort(key=lambda r: (len(r['word']), r['word']))
    
    # Group by hook type for better display
    prefixes = [r for r in results if r['hook_type'] == 'prefix']
    suffixes = [r for r in results if r['hook_type'] == 'suffix']
    
    print(f"=== PREFIX HOOKS ({len(prefixes)} words) ===")
    for r in prefixes[:20]:  # Show first 20
        print(f"  {r['word']:20s} (len={len(r['word']):2d}) + prefix '{r['hook_letter']}' → {r['result_word']}")
    if len(prefixes) > 20:
        print(f"  ... and {len(prefixes) - 20} more")
    
    print(f"\n=== SUFFIX HOOKS ({len(suffixes)} words) ===")
    for r in suffixes[:20]:  # Show first 20
        print(f"  {r['word']:20s} (len={len(r['word']):2d}) + suffix '{r['hook_letter']}' → {r['result_word']}")
    if len(suffixes) > 20:
        print(f"  ... and {len(suffixes) - 20} more")
    
    # Check if EAU is in the results
    print("\n=== VERIFICATION ===")
    eau_result = next((r for r in results if r['word'] == 'EAU'), None)
    if eau_result:
        print(f"EAU: {eau_result['hook_type']} '{eau_result['hook_letter']}' → {eau_result['result_word']}")
    else:
        print("EAU not found in results (may have more than one hook)")
        # Let's check EAU specifically
        words = load_dictionary(dictionary_path)
        if 'EAU' in words:
            alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            prefix_hooks = [l for l in alphabet if l + 'EAU' in words]
            suffix_hooks = [l for l in alphabet if l != 'S' and 'EAU' + l in words]
            print(f"  EAU prefix hooks: {prefix_hooks}")
            print(f"  EAU suffix hooks: {suffix_hooks}")
    
    # Save all results to a file
    output_file = '/home/cph/scrabble/scrabble/dictionary/one_hook_words_output.txt'
    with open(output_file, 'w') as f:
        f.write(f"Words with exactly one hook (ignoring 's' suffix)\n")
        f.write(f"After removing plural duplicates: {len(results)} words\n")
        f.write(f"Sorted by word length (shortest first)\n\n")
        
        f.write(f"PREFIX HOOKS ({len(prefixes)} words):\n")
        for r in prefixes:
            f.write(f"  {r['word']:20s} (len={len(r['word']):2d}) + prefix '{r['hook_letter']}' → {r['result_word']}\n")
        
        f.write(f"\nSUFFIX HOOKS ({len(suffixes)} words):\n")
        for r in suffixes:
            f.write(f"  {r['word']:20s} (len={len(r['word']):2d}) + suffix '{r['hook_letter']}' → {r['result_word']}\n")
    
    print(f"\nFull results saved to: {output_file}")

if __name__ == '__main__':
    main()

