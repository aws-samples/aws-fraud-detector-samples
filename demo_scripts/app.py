from click_web import create_click_web_app
import create_afd_resources

app = create_click_web_app(create_afd_resources, create_afd_resources.cli)