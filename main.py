import sys
import os
import time
import re
import argparse
import praw
from praw.exceptions import RedditAPIException, PRAWException

secrets_loaded = False
from secrets import *

if not secrets_loaded:
    print("Missing secrets.py. Aborting")
    sys.exit(1)


def read_faq_file(keyword):
    """Read FAQ file for the given keyword by parsing triggers.md, fallback to unknown.md if not found."""
    keyword = keyword.lower()
    
    # First, try to find the keyword in triggers.md
    try:
        with open("./triggers.md", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('- [') and '](' in line:
                    # Parse line format: - [keyword1, keyword2](./path/to/file.md)
                    # Extract keywords between [ and ]
                    keywords_start = line.find('[') + 1
                    keywords_end = line.find(']')
                    if keywords_start > 0 and keywords_end > keywords_start:
                        keywords_str = line[keywords_start:keywords_end]
                        keywords = [k.strip().lower() for k in keywords_str.split(',')]
                        
                        # Check if our keyword matches any in this line
                        if keyword in keywords:
                            # Extract file path between ( and )
                            path_start = line.find('](') + 2
                            path_end = line.find(')', path_start)
                            if path_start > 1 and path_end > path_start:
                                faq_path = line[path_start:path_end]
                                break
                else:
                    continue
            else:
                # Keyword not found in triggers.md, use default
                faq_path = "./template/unknown.md"
    except FileNotFoundError:
        print("Warning: triggers.md not found, using default unknown.md")
        faq_path = "./template/unknown.md"
    except Exception as e:
        print(f"Error parsing triggers.md: {e}")
        faq_path = "./template/unknown.md"
    
    # Now read the determined FAQ file
    try:
        with open(faq_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Sorry, I couldn't find the FAQ file."
    except Exception as e:
        print(f"Error reading FAQ file: {e}")
        return "Sorry, there was an error reading the FAQ."


def read_footer():
    """Read the footer content."""
    try:
        with open("./template/footer.md", 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"Error reading footer: {e}")
        return ""


def extract_keyword(message_body):
    """Extract keyword from message that starts with /u/xeqtbot."""
    # Case-insensitive pattern to match /u/xeqtbot followed by space and keyword
    pattern = r'(?i)/?u/xeqtbot\s+([a-zA-Z_-]+)'
    match = re.search(pattern, message_body.strip())
    
    if match:
        return match.group(1).lower()
    return None


def create_response(keyword):
    """Create the full response by combining FAQ content and footer."""
    faq_content = read_faq_file(keyword)
    footer_content = read_footer()
    
    if footer_content:
        return f"{faq_content}\n\n*****\n\n{footer_content}"
    return faq_content


def main():
    """Main bot function."""
    try:
        # Initialize Reddit instance
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            username=BOT_USER,
            password=BOT_PASSWORD,
            user_agent="Automatic response to FAQs about XEQT, for primary use in /r/justbuyxeqt"
        )
        
        print(f"Bot started as u/{reddit.user.me()}")
        
        # Process unread messages
        for message in reddit.inbox.unread(limit=None):
            if not message.was_comment:
                continue  # Skip direct messages, only process comments
            
            try:
                keyword = extract_keyword(message.body)
                
                if keyword:
                    print(f"Processing message with keyword: {keyword}")
                    
                    response = create_response(keyword)
                    
                    # Mark as read
                    message.mark_read()

                    # Reply to the message
                    message.reply(response)
                    
                    print(f"Replied to message with keyword: {keyword}")
                    
                    # Add delay to avoid rate limiting
                    time.sleep(5)
                else:
                    # Mark non-matching messages as read without responding
                    message.mark_read()
                    
            except RedditAPIException as e:
                print(f"Reddit API error processing message: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error processing message: {e}")
                continue
        
        print("Finished processing messages")
        
    except PRAWException as e:
        print(f"PRAW error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="XEQT Reddit Bot - Responds to FAQ triggers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py                    # Run the Reddit bot
  python3 main.py dividend           # Test response for 'dividend' keyword
  python3 main.py --keyword lumpsum  # Test response for 'lumpsum' keyword
        """
    )
    
    parser.add_argument(
        'keyword', 
        nargs='?', 
        help='Test keyword to generate response for (skips Reddit bot mode)'
    )
    
    parser.add_argument(
        '--keyword', '-k',
        dest='keyword_flag',
        help='Alternative way to specify test keyword'
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    # Determine the keyword from either positional or flag argument
    test_keyword = args.keyword or args.keyword_flag
    
    if test_keyword:
        # Local testing mode - generate and print response
        print(f"Testing response for keyword: '{test_keyword}'")
        print("=" * 60)
        response = create_response(test_keyword)
        print(response)
    else:
        # Normal Reddit bot mode
        main()

