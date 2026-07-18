def test_package_imports_and_reports_version():
    import confluence_engine
    assert confluence_engine.__version__ == "0.1.0"
