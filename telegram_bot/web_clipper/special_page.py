class SpecialPage:

    def __init__(self, type_id, default_database, default_title, url_pattern, default_icon=None, title_pattern=None,
                 selenium=False, type_select_option=None, embeddable_content=False, embeddable_video=False,
                 title_html_tag=None):
        self.type_id = type_id
        self.url_pattern = url_pattern
        self.title_pattern = title_pattern
        self.title_html_tag = title_html_tag
        self.selenium = selenium

        # Notion props
        self.default_title = default_title
        self.default_database = default_database
        self.default_icon = default_icon
        self.type_select_option = type_select_option
        self.embeddable_content = embeddable_content
        self.embeddable_video = embeddable_video

    type = None
