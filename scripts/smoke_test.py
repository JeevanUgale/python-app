import sys
try:
    import python_app
    assert hasattr(python_app, 'create_app'), 'create_app not found'
    print('SMOKE: import OK and create_app found')
    sys.exit(0)
except Exception as e:
    print('SMOKE test failed:', e)
    sys.exit(2)
