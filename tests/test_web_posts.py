from app.routers.posts import TOPIC_OPTIONS, _generate_tweet_text


def test_generate_tweet_uses_known_topic_template():
    text = _generate_tweet_text("product-launch")

    assert "product launch" in text.lower()
    assert len(text) <= 280



def test_generate_tweet_supports_custom_topic():
    text = _generate_tweet_text("AI marketing workflows")

    assert "ai marketing workflows" in text.lower()
    assert len(text) <= 280



def test_topic_options_include_auto_post_choices():
    topic_ids = {item["id"] for item in TOPIC_OPTIONS}

    assert {"product-launch", "industry-insight", "community-update"}.issubset(topic_ids)
