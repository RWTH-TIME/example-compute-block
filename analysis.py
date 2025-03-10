from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from collections import Counter
from textblob import TextBlob

# List of common stopwords
stopwords = set([
    "the", "and", "a", "of", "to", "in", "on", "for", "with", "as", "is", "at",
    "which", "by", "an", "be", "this", "that", "it", "from", "you", "he",
    "she", "we", "they", "or", "but", "not", "are", "were", "been", "being",
    "their", "have", "all", "than", "upon", "any", "those", "its", "has",
    "was",
])


def word_frequency(text, use_stopwords: bool = True):
    words = text.lower().split()

    if use_stopwords:
        words = [word for word in words if word not in stopwords]

    return (
        Counter(words).most_common()[:20],
        Counter(words).most_common()[-20:]
    )


def sentiment_analysis(text):
    return TextBlob(text).sentiment


def generate_pdf(
        word_stats,
        filename="word_frequency_statistics.pdf",
        most_common: bool = True
):
    # Create a PDF canvas
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 40, "Word Frequency Statistics")

    # Draw a separator line
    c.setLineWidth(1)
    c.line(50, height - 50, width - 50, height - 50)

    # Set the section title based on the most_common flag
    section_title = "Most Common Words" if most_common else "Least Common Words"
    print(section_title)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 70, section_title)

    # Set font for the word list
    c.setFont("Helvetica", 10)

    # Position for the first word
    y_position = height - 90

    # Add the word-frequency pairs to the PDF
    for word, freq in word_stats:
        c.drawString(100, y_position, f"{word}: {freq}")
        y_position -= 15

    # Save the PDF
    c.save()


if __name__ == "__main__":
    with open("output.txt", "r", encoding="utf-8") as file:
        text = file.read()
    stats = word_frequency(text)[0]
    generate_pdf(stats)
