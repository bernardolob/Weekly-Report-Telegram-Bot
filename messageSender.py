import re
import html
import logging
from telegram.error import TelegramError

# Telegram rejects messages longer than 4096 characters (counted after HTML parsing).
# Keep a margin below the limit.
MAX_MESSAGE_LENGTH = 4000

TAG_PATTERN = re.compile(r"<(/?)([a-zA-Z0-9-]+)[^>]*>")
BARE_AMPERSAND_PATTERN = re.compile(r"&(?!(?:amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)")


def escapeBareAmpersands(text: str) -> str:
    # "Human Rights & AI" -> "Human Rights &amp; AI", required by parse_mode="HTML"
    return BARE_AMPERSAND_PATTERN.sub("&amp;", text)


def visibleLength(text: str) -> int:
    # Length as Telegram counts it: tags removed, entities decoded, UTF-16 code units
    plain = html.unescape(TAG_PATTERN.sub("", text))
    return len(plain.encode("utf-16-le")) // 2


def splitHtmlMessage(text: str, limit: int = MAX_MESSAGE_LENGTH) -> list[str]:
    # Splits on line breaks. Tags still open at a split point are closed at the end
    # of the chunk and reopened at the start of the next one.
    chunks = []
    current = ""
    openTags = []  # list of (tag name, original opening tag)

    for line in text.split("\n"):
        reopen = "".join(tag for _, tag in openTags)
        candidate = line if not current else current + "\n" + line

        if current and visibleLength(candidate) > limit:
            closing = "".join(f"</{name}>" for name, _ in reversed(openTags))
            chunks.append(current + closing)
            current = reopen + line
        else:
            current = candidate

        for match in TAG_PATTERN.finditer(line):
            isClosing, name = match.group(1), match.group(2).lower()
            if not isClosing:
                openTags.append((name, match.group(0)))
            elif openTags and openTags[-1][0] == name:
                openTags.pop()

    if current.strip():
        chunks.append(current)
    return chunks


async def sendLongHtmlMessage(bot, chat_id, text, pin=False) -> bool:
    # Sends a (possibly long) HTML message in several parts. Pins the first part only
    # after every part is sent, so the pin notice appears below the whole message.
    # Returns False and logs Telegram's error description if anything fails.
    if not text:
        logging.error(f"Message for chat {chat_id} is empty (cache refresh failed?). Nothing sent.")
        return False

    chunks = splitHtmlMessage(escapeBareAmpersands(text))
    if len(chunks) > 1:
        logging.info(f"Message has {visibleLength(text)} characters. Sending in {len(chunks)} parts.")

    try:
        sentMessages = []
        for chunk in chunks:
            sentMessages.append(await bot.send_message(
                chat_id=chat_id,
                text=chunk,
                disable_web_page_preview=True,
                parse_mode="HTML"
            ))
        if pin:
            await sentMessages[0].pin()
    except TelegramError as e:
        logging.error(f"Failed to send message to chat {chat_id}: {e}")
        return False
    return True
