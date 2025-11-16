import os
import tempfile
from jee_data_base import DataBase, Filter, pdfy


def test_full_pipeline():
    """
    Full end-to-end integration test:
    - Load database
    - Apply filters
    - Run clustering
    - Render HTML
    """

    # --- Step 1: Load DB ---
    db = DataBase()

    # Ensure chapters loaded correctly
    assert isinstance(db.chapters_dict, dict)
    assert len(db.chapters_dict) > 0

    # --- Step 2: Create filter ---
    f = Filter(db.chapters_dict)

    possible = f.get_possible_filter_values()
    assert "chapter" in possible
    assert len(possible["chapter"]) > 0

    # Select any available chapter dynamically
    test_chapter = possible["chapter"][0]

    # --- Step 3: Filter ---
    qset = (
        f.by_chapter(test_chapter)
         .by_n_last_yrs(2)
         .get()
    )

    # Should return at least one question
    assert len(qset) > 0

    # --- Step 4: Cluster ---
    f.current_set = qset
    cluster = f.cluster()

    # Clustering must return a dict or list
    assert cluster is not None
    assert len(cluster) > 0

    # --- Step 5: Render HTML ---
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "test.html")
        pdfy.render_cluster_to_html_skim(cluster, out, "Test Title")

        # html file must exist
        assert os.path.exists(out)

        # and be non-empty
        assert os.path.getsize(out) > 10
    
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td,"alcohols-phenols-and-ethers")
        f.render_chap_last5yrs(td,"alcohols-phenols-and-ethers",skim=False)

        assert os.path.exists(out)
        assert len(os.listdir(out)) > 0