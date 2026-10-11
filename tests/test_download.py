import hashlib
import urllib.request

import pytest

from palmer_penguins.data import ChecksumError, download_raw, sha256sum, verify_checksum

CONTENT = b"species,island\nAdelie,Torgersen\n"
CONTENT_SHA = hashlib.sha256(CONTENT).hexdigest()


def test_sha256sum_known_value(tmp_path):
    f = tmp_path / "abc.txt"
    f.write_bytes(b"abc")
    # эталонное значение SHA-256("abc") из стандарта FIPS 180
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert sha256sum(f) == expected


def test_verify_checksum_detects_one_changed_byte(tmp_path):
    f = tmp_path / "data.csv"
    f.write_bytes(CONTENT.replace(b"Adelie", b"Adelia"))
    with pytest.raises(ChecksumError):
        verify_checksum(f, CONTENT_SHA)


def test_download_accepts_correct_file(tmp_path, monkeypatch):
    def fake_urlretrieve(url, filename):
        filename.write_bytes(CONTENT)

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    path = tmp_path / "raw" / "penguins.csv"
    download_raw(url="http://example", path=path, expected_sha256=CONTENT_SHA)
    assert path.read_bytes() == CONTENT
    assert not (tmp_path / "raw" / "penguins.csv.part").exists()


def test_download_rejects_wrong_file_and_leaves_nothing(tmp_path, monkeypatch):
    def fake_urlretrieve(url, filename):
        filename.write_bytes(b"<html>404 Not Found</html>")

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    path = tmp_path / "raw" / "penguins.csv"
    with pytest.raises(ChecksumError):
        download_raw(url="http://example", path=path, expected_sha256=CONTENT_SHA)
    assert list(path.parent.iterdir()) == []


def test_existing_file_is_checked_without_network(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("сеть не должна использоваться")

    monkeypatch.setattr(urllib.request, "urlretrieve", no_network)
    path = tmp_path / "penguins.csv"
    path.write_bytes(CONTENT)
    assert download_raw(path=path, expected_sha256=CONTENT_SHA) == path

    path.write_bytes(CONTENT + b"Gentoo,Biscoe\n")  # «ручная правка» сырых данных
    with pytest.raises(ChecksumError):
        download_raw(path=path, expected_sha256=CONTENT_SHA)
