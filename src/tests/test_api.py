def register_user(
    client,
    username="testuser",
    email="test@example.com",
    password="secret123",
):
    return client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )


def login_user(
    client,
    email="test@example.com",
    password="secret123",
):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# --------------------------------------------------
# Health
# --------------------------------------------------


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --------------------------------------------------
# Authentication
# --------------------------------------------------


def test_register_user(client):
    response = register_user(client)

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"


def test_register_invalid_email(client):
    response = register_user(
        client,
        email="not-an-email",
    )

    assert response.status_code == 422


def test_register_duplicate_user(client):
    register_user(client)

    response = register_user(client)

    assert response.status_code == 409


def test_login_user(client):
    register_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    register_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 401


def test_get_current_user(client):
    register_user(client)

    token = login_user(client)

    response = client.get(
        "/users/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"


def test_get_current_user_without_token(client):
    response = client.get("/users/me")

    assert response.status_code == 401


# --------------------------------------------------
# Notes - Create / Read
# --------------------------------------------------


def test_create_note(client):
    register_user(client)

    token = login_user(client)

    response = client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "My first note",
            "content": "This is my first note.",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "My first note"
    assert response.json()["content"] == "This is my first note."
    assert response.json()["archived"] is False


def test_list_notes(client):
    register_user(client)

    token = login_user(client)

    client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Note one",
            "content": "First note",
        },
    )

    client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Note two",
            "content": "Second note",
        },
    )

    response = client.get(
        "/notes",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_note(client):
    register_user(client)

    token = login_user(client)

    create_response = client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "My note",
            "content": "Note content",
        },
    )

    note_id = create_response.json()["id"]

    response = client.get(
        f"/notes/{note_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == note_id
    assert response.json()["title"] == "My note"


# --------------------------------------------------
# Notes - Update / Delete
# --------------------------------------------------


def test_update_note(client):
    register_user(client)

    token = login_user(client)

    create_response = client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Original title",
            "content": "Original content",
        },
    )

    note_id = create_response.json()["id"]

    response = client.patch(
        f"/notes/{note_id}",
        headers=auth_headers(token),
        json={
            "title": "Updated title",
            "content": "Updated content",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["content"] == "Updated content"


def test_delete_note(client):
    register_user(client)

    token = login_user(client)

    create_response = client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Delete me",
            "content": "This note will be deleted.",
        },
    )

    note_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/notes/{note_id}",
        headers=auth_headers(token),
    )

    assert delete_response.status_code == 200

    get_response = client.get(
        f"/notes/{note_id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


# --------------------------------------------------
# Notes - Archive
# --------------------------------------------------


def test_archive_note(client):
    register_user(client)

    token = login_user(client)

    create_response = client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Archive me",
            "content": "This note will be archived.",
        },
    )

    note_id = create_response.json()["id"]

    response = client.post(
        f"/notes/{note_id}/archive",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["archived"] is True


def test_archived_note_not_in_normal_list(client):
    register_user(client)

    token = login_user(client)

    create_response = client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Archive me",
            "content": "Archived content",
        },
    )

    note_id = create_response.json()["id"]

    client.post(
        f"/notes/{note_id}/archive",
        headers=auth_headers(token),
    )

    response = client.get(
        "/notes",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_list_archived_notes(client):
    register_user(client)

    token = login_user(client)

    create_response = client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Archived note",
            "content": "Archived content",
        },
    )

    note_id = create_response.json()["id"]

    client.post(
        f"/notes/{note_id}/archive",
        headers=auth_headers(token),
    )

    response = client.get(
        "/notes?archived=true",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["archived"] is True


def test_unarchive_note(client):
    register_user(client)

    token = login_user(client)

    create_response = client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Unarchive me",
            "content": "This note will return.",
        },
    )

    note_id = create_response.json()["id"]

    client.post(
        f"/notes/{note_id}/archive",
        headers=auth_headers(token),
    )

    response = client.post(
        f"/notes/{note_id}/unarchive",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["archived"] is False


# --------------------------------------------------
# Notes - Search
# --------------------------------------------------


def test_search_notes(client):
    register_user(client)

    token = login_user(client)

    client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Python Backend",
            "content": "Learning FastAPI",
        },
    )

    client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Shopping",
            "content": "Buy groceries",
        },
    )

    response = client.get(
        "/notes?search=python",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Python Backend"


def test_search_notes_content(client):
    register_user(client)

    token = login_user(client)

    client.post(
        "/notes",
        headers=auth_headers(token),
        json={
            "title": "Backend",
            "content": "FastAPI is useful for APIs",
        },
    )

    response = client.get(
        "/notes?search=FastAPI",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# --------------------------------------------------
# Notes - Pagination
# --------------------------------------------------


def test_notes_pagination(client):
    register_user(client)

    token = login_user(client)

    for number in range(5):
        client.post(
            "/notes",
            headers=auth_headers(token),
            json={
                "title": f"Note {number}",
                "content": f"Content {number}",
            },
        )

    response = client.get(
        "/notes?limit=2&offset=0",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(
        "/notes?limit=2&offset=2",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


# --------------------------------------------------
# Authorization / Ownership
# --------------------------------------------------


def test_user_cannot_access_another_users_note(client):
    register_user(
        client,
        username="userone",
        email="userone@example.com",
    )

    user_one_token = login_user(
        client,
        email="userone@example.com",
    )

    create_response = client.post(
        "/notes",
        headers=auth_headers(user_one_token),
        json={
            "title": "Private note",
            "content": "Only user one should see this.",
        },
    )

    note_id = create_response.json()["id"]

    register_user(
        client,
        username="usertwo",
        email="usertwo@example.com",
    )

    user_two_token = login_user(
        client,
        email="usertwo@example.com",
    )

    response = client.get(
        f"/notes/{note_id}",
        headers=auth_headers(user_two_token),
    )

    assert response.status_code == 404


def test_user_cannot_update_another_users_note(client):
    register_user(
        client,
        username="userone",
        email="userone@example.com",
    )

    user_one_token = login_user(
        client,
        email="userone@example.com",
    )

    create_response = client.post(
        "/notes",
        headers=auth_headers(user_one_token),
        json={
            "title": "Private note",
            "content": "Private content",
        },
    )

    note_id = create_response.json()["id"]

    register_user(
        client,
        username="usertwo",
        email="usertwo@example.com",
    )

    user_two_token = login_user(
        client,
        email="usertwo@example.com",
    )

    response = client.patch(
        f"/notes/{note_id}",
        headers=auth_headers(user_two_token),
        json={
            "title": "Hacked title",
        },
    )

    assert response.status_code == 404


def test_user_cannot_delete_another_users_note(client):
    register_user(
        client,
        username="userone",
        email="userone@example.com",
    )

    user_one_token = login_user(
        client,
        email="userone@example.com",
    )

    create_response = client.post(
        "/notes",
        headers=auth_headers(user_one_token),
        json={
            "title": "Private note",
            "content": "Private content",
        },
    )

    note_id = create_response.json()["id"]

    register_user(
        client,
        username="usertwo",
        email="usertwo@example.com",
    )

    user_two_token = login_user(
        client,
        email="usertwo@example.com",
    )

    response = client.delete(
        f"/notes/{note_id}",
        headers=auth_headers(user_two_token),
    )

    assert response.status_code == 404


def test_notes_limit_cannot_exceed_100(client):
    register_user(client)

    token = login_user(client)

    response = client.get(
        "/notes?limit=101",
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_notes_offset_cannot_be_negative(client):
    register_user(client)

    token = login_user(client)

    response = client.get(
        "/notes?offset=-1",
        headers=auth_headers(token),
    )

    assert response.status_code == 422    