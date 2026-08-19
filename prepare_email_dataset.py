import os
import email
import pandas as pd
from email import policy
from email.parser import BytesParser


# Dataset folders
HAM_FOLDERS = ["easy-ham", "hard-ham"]
SPAM_FOLDER = "spam"

OUTPUT_FILE = os.path.join("dataset", "email_dataset.csv")


def extract_email_text(file_path):
    """
    Email file se subject + body extract karta hai.
    """

    try:
        with open(file_path, "rb") as f:
            message = BytesParser(policy=policy.default).parse(f)

        subject = message.get("subject", "")
        body = ""

        if message.is_multipart():

            for part in message.walk():

                content_type = part.get_content_type()

                if content_type == "text/plain":

                    try:
                        body = part.get_content()
                    except Exception:
                        body = ""

                    break

        else:

            try:
                body = message.get_content()
            except Exception:
                body = ""

        text = f"{subject} {body}".strip()

        return text

    except Exception as e:

        print(f"Could not process {file_path}: {e}")
        return ""


def process_folder(folder_name, label, data):

    """
    Folder ke andar aur uske subfolders ke andar
    saari email files process karta hai.
    """

    folder_path = os.path.join("dataset", folder_name)

    if not os.path.exists(folder_path):

        print(f"Folder not found: {folder_path}")
        return

    print(f"\nProcessing {folder_name}...")

    processed = 0

    # Walk through all subfolders
    for root, dirs, files in os.walk(folder_path):

        for filename in files:

            file_path = os.path.join(root, filename)

            text = extract_email_text(file_path)

            if text:

                data.append({
                    "label": label,
                    "text": text
                })

                processed += 1

    print(f"Finished {folder_name}")
    print(f"Emails processed: {processed}")


def main():

    data = []

    # Genuine emails
    for folder in HAM_FOLDERS:

        process_folder(
            folder,
            0,
            data
        )

    # Spam emails
    process_folder(
        SPAM_FOLDER,
        1,
        data
    )

    # Check whether emails were found
    if not data:

        print("\nERROR: No emails were processed.")
        print("Please check the dataset folders.")
        return

    # Create DataFrame
    df = pd.DataFrame(data)

    # Remove empty text
    df = df.dropna(subset=["text"])

    df = df[
        df["text"].str.strip() != ""
    ]

    # Remove duplicate emails
    df = df.drop_duplicates(
        subset=["text"]
    )

    # Shuffle dataset
    df = df.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    # Save CSV
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # Print statistics
    print("\nDataset created successfully!")

    print(f"Total emails: {len(df)}")

    print(
        f"Ham emails: "
        f"{sum(df['label'] == 0)}"
    )

    print(
        f"Spam emails: "
        f"{sum(df['label'] == 1)}"
    )

    print(
        f"\nSaved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()