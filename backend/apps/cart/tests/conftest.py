import pytest

from django.contrib.sessions.middleware import SessionMiddleware

@pytest.fixture
def request_with_session(rf):
    request = rf.get('/')
    
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    return request