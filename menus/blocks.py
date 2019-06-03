from wagtail.wagtailcore import blocks
from django import forms


def get_request(parent_context):
    try:
        return parent_context['request']
    except (AttributeError, KeyError):
        # Allows caching of site root paths
        return SubstituteRequest()


def get_current_site(request):
    return request.site


def get_page_link_text(page):
    return page.title


class SubstituteRequest:
    pass


class ReverseURLBlock(blocks.CharBlock):
    """
    A block that validates the value to ensure that it is a reversible
    Django URL.

    NOTE: Needs work
    """
    pass


class BaseLinkBlock(blocks.StructBlock):
    text = blocks.CharBlock()
    url_fragment = blocks.CharBlock(required=False)
    list_item_classes = blocks.CharBlock(required=False)
    link_classes = blocks.CharBlock(required=False)

    class Meta:
        icon = 'link'
        template = 'menus/blocks/link.html'


class BaseLinkListBlock(blocks.StructBlock):

    class Meta:
        icon = 'list-ul'
        template = 'menus/blocks/link_list.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['links'] = self.get_links(value, parent_context)
        return context

    def get_links(self, value, parent_context):
        raise NotImplementedError


class LinkGeneratorChooserBlock(blocks.ChooserBlock):
    """
    A block that lists registered LinkGenerator classes as options.

    NOTE: Needs work
    """
    target_model = None
    widget = forms.Select

    # Return the key value for the select field
    def value_for_form(self, value):
        if isinstance(value, self.target_model):
            return value.pk
        else:
            return value


class LinkGeneratorBlock(BaseLinkListBlock):
    generator = LinkGeneratorChooserBlock()

    def get_links(self, value, parent_context):
        return value['generator'].get_links(parent_context)


class ChildPageLinksBlock(BaseLinkListBlock):
    parent_page = blocks.PageChooserBlock()

    def get_links(self, value, parent_context):
        parent_page = value['parent_page']
        request = get_request(parent_context)
        current_site = get_current_site(request)
        for page in parent_context['pages_by_parent'].get(parent_page.id, ()):
            yield {
                'url': page.get_url(request, current_site),
                'text': get_page_link_text(page),
            }


class PageLinkBlock(BaseLinkBlock):
    page = blocks.PageChooserBlock()
    link_text = blocks.CharBlock(required=False)


class DjangoURLLinkBlock(BaseLinkBlock):
    url_name = blocks.ReverseURLBlock()


class ExternalLinkBlock(BaseLinkBlock):
    url = blocks.URLBlock()


class CustomLinkBlock(BaseLinkBlock):
    url = blocks.CharBlock(required=False)


class LevelFourLinkStreamBlock(blocks.StreamBlock):
    page_link = PageLinkBlock()
    django_url_link = DjangoURLLinkBlock()
    external_link = ExternalLinkBlock()
    custom_link = CustomLinkBlock()
    link_list_from_child_pages = ChildPageLinksBlock()
    link_list_from_generator = LinkGeneratorBlock()


class LevelThreePageLinkBlock(PageLinkBlock):
    children = LevelFourLinkStreamBlock()


class LevelThreeDjangoURLLinkBlock(DjangoURLLinkBlock):
    children = LevelFourLinkStreamBlock()


class LevelThreeExternalLinkBlock(ExternalLinkBlock):
    children = LevelFourLinkStreamBlock()


class LevelThreeCustomLinkBlock(CustomLinkBlock):
    children = LevelFourLinkStreamBlock()


class LevelThreeLinkStreamBlock(blocks.StreamBlock):
    page_link = LevelThreeDjangoURLLinkBlock()
    django_url_link = LevelThreeDjangoURLLinkBlock()
    external_link = LevelThreeExternalLinkBlock()
    custom_link = LevelThreeCustomLinkBlock()
    link_list_from_child_pages = ChildPageLinksBlock()
    link_list_from_generator = LinkGeneratorBlock()


class LevelTwoPageLinkBlock(PageLinkBlock):
    children = LevelThreeLinkStreamBlock()


class LevelTwoDjangoURLLinkBlock(DjangoURLLinkBlock):
    children = LevelThreeLinkStreamBlock()


class LevelTwoExternalLinkBlock(ExternalLinkBlock):
    children = LevelThreeLinkStreamBlock()


class LevelTwoCustomLinkBlock(CustomLinkBlock):
    children = LevelThreeLinkStreamBlock()


class LevelTwoLinkStreamBlock(blocks.StreamBlock):
    page_link = LevelTwoDjangoURLLinkBlock()
    django_url_link = LevelTwoDjangoURLLinkBlock()
    external_link = LevelTwoExternalLinkBlock()
    custom_link = LevelTwoCustomLinkBlock()


class LevelOnePageLinkBlock(PageLinkBlock):
    children = LevelTwoLinkStreamBlock()


class LevelOneDjangoURLLinkBlock(DjangoURLLinkBlock):
    children = LevelTwoLinkStreamBlock()


class LevelOneExternalLinkBlock(ExternalLinkBlock):
    children = LevelTwoLinkStreamBlock()


class LevelOneCustomLinkBlock(CustomLinkBlock):
    children = LevelTwoLinkStreamBlock()


class LinkStreamBlock(blocks.StreamBlock):
    page_link = LevelOnePageLinkBlock()
    django_url_link = LevelOneDjangoURLLinkBlock()
    external_link = LevelOneExternalLinkBlock()
    custom_link = LevelOneCustomLinkBlock()
