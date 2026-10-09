def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
):
    # Clean up the extracted PDF text
    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    chunks = []
    current_words = []

    for line in lines:

        line_words = line.split()

        # Add words from the current line
        for word in line_words:

            current_words.append(word)

            # Check whether the chunk reached its target size
            current_text = " ".join(current_words)

            if len(current_text) >= chunk_size:

                chunks.append(current_text)

                # Keep the last few words as overlap
                overlap_words = []
                overlap_length = 0

                for previous_word in reversed(current_words):
                    overlap_words.insert(0, previous_word)
                    overlap_length += len(previous_word) + 1

                    if overlap_length >= overlap:
                        break

                current_words = overlap_words

    # Add remaining words
    if current_words:
        final_chunk = " ".join(current_words)

        if final_chunk not in chunks:
            chunks.append(final_chunk)

    return chunks