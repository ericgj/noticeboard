
from util.decode import decoded_base64
from model.article import Request, Article

from adapter import pubsub
import env

creds = env.service_account_credentials()
pubsub_client = pubsub.publisher_client(creds)

def init(*args):
    pubsub.create_topics(pubsub_client, env.project_id(),
        [ env.pubsub_topic() ]
    )

@decoded_base64(Request.from_json) 
def parse(req, ctx):
    pubsub.publish(pubsub_client, env.pubsub_topic(), parse_value(req).to_json())
    return ''

def parse_value(req):
    return Article.fetch(req)


