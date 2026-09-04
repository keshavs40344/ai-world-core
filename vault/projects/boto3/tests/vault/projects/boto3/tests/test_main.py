import pytest
from src.main import main


@pytest.fixture(scope='module')
def test_file_path():
    return 'tests/vault/projects/boto3/tests/test_main.py'
@pytest.mark.parametrize('file_path', [test_file_path()])
def test_main(file_path):
    assert main() == '', f'Expected main() to return nothing, but got {main()}'
