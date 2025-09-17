import sys
import os
import time
import re
import praw
from praw.exceptions import RedditAPIException, PRAWException

secrets_loaded = False
from secrets import *

if not secrets_loaded:
    print("Missing secrets.py. Aborting")
    sys.exit(1)


def read_faq_file(keyword):
    """Read FAQ file for the given keyword, fallback to unknown.md if not found."""
    faq_path = f"./faq/{keyword.lower()}.md"
    
    if not os.path.exists(faq_path):
        faq_path = "./faq/unknown.md"
    
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
        with open("./footer.md", 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"Error reading footer: {e}")
        return ""


def extract_keyword(message_body):
    """Extract keyword from message that starts with /u/xeqtbot."""
    # Case-insensitive pattern to match /u/xeqtbot followed by space and keyword
    pattern = r'(?i)^/?u/xeqtbot\s+(\w+)'
    match = re.search(pattern, message_body.strip())
    
    if match:
        return match.group(1).lower()
    return None


def create_response(keyword):
    """Create the full response by combining FAQ content and footer."""
    faq_content = read_faq_file(keyword)
    footer_content = read_footer()
    
    if footer_content:
        return f"{faq_content}\n\n{footer_content}"
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
                    
                    # Reply to the message
                    message.reply(response)
                    
                    # Mark as read
                    message.mark_read()
                    
                    print(f"Replied to message with keyword: {keyword}")
                    
                    # Add delay to avoid rate limiting
                    time.sleep(2)
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


if __name__ == "__main__":
    main()

