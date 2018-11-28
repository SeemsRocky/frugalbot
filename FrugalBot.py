import urllib
import tweepy
import praw
import os
import pdb
import re

# Create the Reddit instance
reddit = praw.Reddit('bot1')

# and login
#reddit.login(USERNAME,PASSWORD)
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

user = api.me()

# Helper method to decide whether or not to reply to a tweet if the status update would be too long
def statusUpdater(title,urlOrText):
    if len(title) + len(urlOrText) > 280:
        api.update_status(f"{title}{urlOrText[:(280-len(submission.title))]}")
        mostRecentTweet = api.user_timeline(count=1)
        api.update_status(f"{urlOrText}", in_reply_to_status_id=mostRecentTweet[0].id)
    else:
        api.update_status(f"{title} {urlOrText}")

# Helper method to decide which links to post
def statusUpdateDecider(title, urlOrText, text=""):
    if submission.url.find("reddit") >= 0:
        posStart = submission.selftext.find("(https")
        posEnd = submission.selftext.find(")", posStart)
        if posStart > -1:
            correctLink = submission.selftext[posStart + 1:posEnd]
            goodLink = True
        else:
            correctLink = re.search("(?P<url>https?://[^\s]+)", submission.selftext)
            goodLink = False
        if goodLink:
            statusUpdater(title, urlOrText)
        else:
            if correctLink is not None:
                correctLink = correctLink.group("url")
                statusUpdater(title, correctLink)
            else:
                statusUpdater(title, urlOrText)
    else:
        statusUpdater(title, urlOrText)


# Have we run this code before? If not, create an empty list
if not os.path.isfile(r"C:\Users\baymax\PycharmProjects\frugalbot\posts_checked.txt"):
    posts_checked = []

# If we have run the code before, load the list of posts we have replied to
else:
    # Read the file into a list and remove any empty values
    with open(r"C:\Users\baymax\PycharmProjects\frugalbot\posts_checked.txt", "r") as f:
        posts_checked = f.read()
        posts_checked = posts_checked.split("\n")
        posts_checked = list(filter(None, posts_checked))

print(len(posts_checked))
# Delete the last 200 Unique ids if we reach 500 posts in posts_checked
if len(posts_checked) >= 500:
    posts_checked = posts_checked[:300]

# Get the top 15 values from our subreddit
subreddit1 = reddit.subreddit('frugalmalefashion')
i = 1
for submission in subreddit1.new(limit=15):
    # find specific key values to determine if its a deal
    price = submission.title.find("$") >= 0 or submission.title.find('%') >= 0 or submission.title.find('.')>=0
    notDiscussion = submission.link_flair_text is None or submission.link_flair_text == '[Deal/Sale]'
    # Filter out the submission lists and see if it has been posted before. If not there, then post
    if len(list(filter(lambda x: submission.id == x,posts_checked))) == 0:
        if submission.link_flair_text == '[Deal/Sale]':
            statusUpdateDecider(submission.title, submission.url)
            ''' print("Post #", i)
            print("Title: ", submission.title)
            print("Link: ", submission.url)
            print("Flair_id: ", submission.link_flair_text)
            print("---------------------------------\n")'''
        elif notDiscussion and price:
            if submission.url.find("reddit") >= 0:
                statusUpdateDecider(submission.title, submission.selftext)
                ''' posStart = submission.selftext.find("(https")
                posEnd = submission.selftext.find(")", posStart)
                if posStart > -1:
                    link = submission.selftext[posStart+1:posEnd]
                    linked = True
                else:
                    link = re.search("(?P<url>https?://[^\s]+)", submission.selftext)
                    linked = False
                if linked:
                    print("Post #", i)
                    print("Title: ", submission.title)
                    print("Text: ", link)
                    print("Flair_id: ", submission.link_flair_text)
                    print("---------------------------------\n")
                else:
                    print("Post #", i)
                    print("Title: ", submission.title)
                    if link is not None:
                        link = link.group("url")
                        print("Link in Text: ", link)
                    else:
                        print("Text: ", submission.selftext)
                    print("Flair_id: ", submission.link_flair_text)
                    print("---------------------------------\n")'''
            else:
                statusUpdateDecider(submission.title,submission.url)
                '''print("Post #", i)
                print("Title: ", submission.title)
                print("Link: ", submission.url)
                print("Flair_id: ", submission.link_flair_text)
                print("---------------------------------\n")'''
        posts_checked.append(submission.id)
    i += 1

subreddit2 = reddit.subreddit('sneakerdeals')
for submission in subreddit2.new(limit=15):
    if len(list(filter(lambda x: submission.id == x, posts_checked))) == 0:
        if submission.url.find("reddit") == -1:
            #Parse the html encoding to have a shorter link to fit inside a tweet
            if submission.url.find("mpre") >= 0:
                shortUrl = urllib.parse.unquote(submission.url)
                pos = shortUrl.find("mpre")
                link = shortUrl[pos+5:]
                statusUpdateDecider(submission.title, link)
                '''print("Title: ", submission.title)
                print("Link: ", link)
                print("Flair_id: ", submission.link_flair_text)
                print("---------------------------------\n")'''
            else:
                statusUpdateDecider(submission.title, submission.url)
                
        posts_checked.append(submission.id)


# Write our updated list back to the file
with open(r"C:\Users\baymax\PycharmProjects\frugalbot\posts_checked.txt", "w") as f:
    for post_id in posts_checked:
        f.write(post_id + "\n")

# Remember to follow back our loyal followers
for follower in tweepy.Cursor(api.followers).items():
    follower.follow()
