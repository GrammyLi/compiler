import re
import sys
import tokens as tokens
from tokens import Token, TokenType, symbols, keywords, identifiers


def tokenize(code):
    # Big array of parsed Tokens
    # NOTE: this is a list of Token instances, not just strings
    codeTokens = []

    lines = code.splitlines()
    # TODO: handle multiple escaped lines using \
    # lines = combineEscapedLines(lines)

    for line in lines:
        try:
            # Get the tokens of the current line and add to the big list
            lineTokens = tokenizeLine(line)
            codeTokens += lineTokens
        except Exception as err:
            print(err)
            sys.exit(2)


def tokenizeLine(line):
    """Parse a line into tokens"""
    lineTokens = []

    isInclude = False
    isComment = False

    # We parse characters in a "chunk" with a start and an end
    start = 0
    end = 1

    while end < len(line):
        symbol = matchSymbol(line[end])
        nextSymbol = matchSymbol(line[end + 1])

        # Order of searching:
        # 1. Symbols
        # 2. Keywords
        # 3. Identifiers
        # 4. Numbers

        # TODO: check if we are in an include statement
        # if isInclude:

        # If we are in a multi-line /* */ comment
        if isComment:
            # If the comment is ending
            if symbol == tokens.star and next == tokens.slash:
                isComment = False
                start = end + 2
                end = start
            else:
                start += 1
                end = start
            continue

        # If next two symbols begin a multi-line /* */ comment
        if symbol == tokens.star and next == tokens.slash:
            # Tokenize whatever we found up to this point
            isComment = True
            if start != end:
                previousTokens = tokenizeChunk(line[start:end])
                lineTokens.append(previousTokens)

            continue

        # If next two tokens are //, skip this line, break from while loop, and return
        if symbol == tokens.slash and nextSymbol == tokens.slash:
            break

        # If ending character of chunk is whitespace
        if line[end].isspace():
            # Tokenize whatever we found up to this point, and skip whitespace
            if start != end:
                previousTokens = tokenizeChunk(line[start:end])
                lineTokens.append(previousTokens)

            start = end + 1
            end = start + 1
            print()
            continue

        # If we see a quote, tokenize the entire quoted value as one token
        if symbol in {tokens.doubleQuote, tokens.singleQuote}:
            if symbol == tokens.doubleQuote:
                delimeter = '"'
                kind = tokens.string
            elif symbol == tokens.singleQuote:
                delimeter = "'"
                kind = tokens.character

            # Get the token between the quotes and update our chunk end
            token, end = parseQuote(line, start, kind, delimeter)
            lineTokens.append(token)

            start = end + 1
            end = start + 1
            continue

        # If next character is a symbol
        if symbol is not None:
            # Tokenize whatever we found up to this point
            if start != end:
                previousTokens = tokenizeChunk(line[start:end])
                lineTokens.append(previousTokens)

            # Append the next token
            lineTokens.append(Token(symbol))

            # Move the chunk forward
            start = end + len(symbol.text)
            end = start

            continue

        # If none of the above cases have hit, we must increase our search
        # So we increment our chunk end to include an additional character
        end += 1

    # At this point we have parsed the entire line
    # Flush anything left in the chunk
    previousTokens = tokenizeChunk(line[start:end])
    lineTokens.append(previousTokens)

    # Finally return the list of tokens for this line
    return lineTokens


# TODO: parse a quote: return the value between quotations and the new index
# def parseQuote(text, start, kind, delimeter):


def tokenizeChunk(text):
    """Check if the given text is a keyword, number, or identifier"""
    # Check if it a keyword first
    keyword = matchKeyword(text)
    if keyword is not None:
        return Token(keyword)

    # Check if it a number second
    number = matchNumber(text)
    if number is not None:
        return Token(tokens.number)

    # Check if it an identifier third
    identifier = matchIdentifier(text)
    if identifier is not None:
        return Token(tokens.identifier)

    symbol = matchSymbol(text)
    if symbol is not None:
        return Token(symbol)

    # If it is none of the above, we do not recognize this type
    raise ValueError(f"Unrecognized token: '{text}'")


def matchSymbol(text):
    """Check if a string matches a symbol"""
    for symbol in symbols:
        if symbol.text == text:
            return symbol


def matchKeyword(text):
    """Check if string matches a keyword"""
    for keyword in keywords:
        if keyword.text == text:
            return keyword


def matchIdentifier(text):
    """Check if string matches an identifier"""
    if re.match(r"[a-zA-Z][_a-zA-Z0-9]*$", text):
        return text


def matchNumber(text):
    """Check if string matches a number"""
    if text.isdigit():
        return text