def test_unexpected_route(client):
    response = client.get("/unexpectedroute")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data