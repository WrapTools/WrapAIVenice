# test_document_manager.py

from pathlib import Path
import time
from WrapAIVenice.schema_document import DocumentManager, DocumentDetail

def test_document_manager():
    file_path = Path("test_document.json")

    # Initialize manager and header
    manager = DocumentManager(file_path)
    manager.create_header(document_id="doc_001", system_prompt="Summarize and analyze")

    # Add a summary block
    manager.update_document_detail(
        name="summary",
        model="gpt-4",
        think="I first read the document and summarized it.",
        results="This is a summary.",
        usage={"tokens": 100},
        created=int(time.time()),
        user_prompt="Summarize this document.",
        parameters={"temperature": 0.7}
    )

    # Add an evaluation block
    manager.update_document_detail(
        name="evaluation",
        model="gpt-4",
        think="I evaluated the quality of the summary.",
        results="Summary is accurate and complete.",
        usage={"tokens": 50},
        created=int(time.time()),
        user_prompt="Evaluate the summary for accuracy.",
        parameters={"temperature": 0.5}
    )

    # Add a test block
    manager.update_document_detail(
        name="test",
        model="gpt-3",
        think="I tested the quality of the document.",
        results="Test is accurate and complete.",
        usage={"tokens": 50},
        created=int(time.time()),
        user_prompt="Test for accuracy.",
        parameters={"temperature": 0.6}
    )

    # Save to file
    assert manager.save_to_file()

    # Load from file
    loaded = DocumentManager(file_path)
    assert loaded.load_from_file()

    # Check header
    header = loaded.get_document_header()
    print("Header:", header)

    # Check summary detail
    summary = loaded.get_document_detail("summary")
    print("Summary Block:", summary)

    # Check evaluation detail
    evaluation = loaded.get_document_detail("evaluation")
    print("Evaluation Block:", evaluation)

    # Check test detail
    test = loaded.get_document_detail("test")
    print("Test Block:", test)

    # Check hashes
    summary_hash = loaded.get_hash("summary")
    assert summary_hash
    assert loaded.matches_hash("summary", summary_hash)

    evaluation_hash = loaded.get_hash("evaluation")
    assert evaluation_hash
    assert loaded.matches_hash("evaluation", evaluation_hash)

    test_hash = loaded.get_hash("test")
    assert test_hash
    assert loaded.matches_hash("test", test_hash)


    print("✅ All tests passed.")

if __name__ == "__main__":
    test_document_manager()
