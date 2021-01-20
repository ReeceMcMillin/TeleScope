# Background
Telegram is commonly used as an organizing platform for far-right extremists (as of the time of writing, January 2021). The loose centralization and lack of significant moderation provides a comfortable low-commitment, low-risk platform that can be as difficult to track as is necessary. Naturally, there's value in monitoring the spread of online threads of extremism, so the development of open-source, easy-to-use tools designed to make this data more accessible and standardized is a worthwhile effort.

# Quick Start
After cloning this repo, take a look at what data can be scraped. A TelegramClient() can connect to a *"chat-like"* object, meaning a username (typically follows the *https://t.me/* channel link) is totally acceptable. For standardization purposes an integer ID is prefered but not strictly enforced.
### Finding a Channel ID
* `get_chat_id(client, channel_identifier)` will accept any *"chat-like"* identifier, so it can be used to convert any chat-like object into the channel's distinct ID.
### Scraping a Channel
* `log_channel(client, channel_id, allow_overwrite=False)` will again accept any chat-like identifier, but for reasons of standardization it's preferential to use an integer ID. This will create a `logs/` directory in the source directory and immediately begin attempting to scrape whatever is passed to it.
### Reading the JSON
* The exported JSON contains an enormous amount of metadata about each message. What's interesting to me may not be interesting to you; dig through and see what you find! Note that the files are exported as JSON *arrays*, so your favorite extension may not be able to format the entire document at once.

# Todo
* Type-hinting
* Comprehensive documentation
* More comprehensive, rigorous error handling
* Explicit crawler implementation
* Distinct non-persistent storage of forward-sources
* In-project analysis tool integration

# Note
I'm a full-time student and interesting projects like this one sometimes have to take a backseat. Code contributions are encouraged and this project would be well-suited for a first contribution. If you have questions, I can be reached on Twitter at [reece_io](https://twitter.com/reece_io). Thanks for reading!