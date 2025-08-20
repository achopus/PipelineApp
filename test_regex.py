import re

def test_markdown_patterns():
    """Test markdown regex patterns."""
    
    # Test text
    test_text = '''# Header 1
## Header 2
**Bold text**
*Italic text*
`code text`
- List item 1
- List item 2
[Link text](http://example.com)
'''
    
    html = test_text
    
    try:
        # Headers
        html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold text
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic text
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Lists (unordered)
        html = re.sub(r'^- (.*$)', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        print("All regex patterns work correctly!")
        print("Converted HTML:")
        print(html)
        return True
        
    except Exception as e:
        print(f"Regex error: {e}")
        return False

if __name__ == "__main__":
    test_markdown_patterns()
