from django.contrib.postgres.indexes import GinIndex
from django.db import models
from saleor.store.models import Store
from ..core.db.fields import SanitizedJSONField
from ..core.models import ModelWithMetadata, MultitenantModelWithMetadata, PublishableModelMT
from ..core.permissions import PagePermissions, PageTypePermissions
from ..core.utils.editorjs import clean_editor_js
from ..core.utils.translations import TranslationProxy
from ..seo.models import SeoModel, SeoModelTranslation


class Page(PublishableModelMT, MultitenantModelWithMetadata, SeoModel):
    store = models.ForeignKey(
        Store,
        related_name="pages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tenant_id='store_id'
    slug = models.SlugField(unique=True, max_length=255)
    title = models.CharField(max_length=250)
    page_type = models.ForeignKey(
        "PageType", related_name="pages", on_delete=models.CASCADE
    )
    content = SanitizedJSONField(blank=True, null=True, sanitizer=clean_editor_js)
    created = models.DateTimeField(auto_now_add=True)

    translated = TranslationProxy()

    class Meta(MultitenantModelWithMetadata.Meta):
        ordering = ("slug",)
        permissions = ((PagePermissions.MANAGE_PAGES.codename, "Manage pages."),)
        indexes = [*MultitenantModelWithMetadata.Meta.indexes, GinIndex(fields=["title", "slug"])]

    def __str__(self):
        return self.title


class PageTranslation(SeoModelTranslation):
    language_code = models.CharField(max_length=10)
    page = models.ForeignKey(
        Page, related_name="translations", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    content = SanitizedJSONField(blank=True, null=True, sanitizer=clean_editor_js)

    class Meta:
        ordering = ("language_code", "page", "pk")
        unique_together = (("language_code", "page"),)

    def __repr__(self):
        class_ = type(self)
        return "%s(pk=%r, title=%r, page_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.title,
            self.page_id,
        )

    def __str__(self):
        return self.title if self.title else str(self.pk)


class PageType(MultitenantModelWithMetadata):
    store = models.ForeignKey(
        Store,
        related_name="page_types",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tenant_id='store_id'
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)

    class Meta(MultitenantModelWithMetadata.Meta):
        ordering = ("slug",)
        permissions = (
            (
                PageTypePermissions.MANAGE_PAGE_TYPES_AND_ATTRIBUTES.codename,
                "Manage page types and attributes.",
            ),
        )
        indexes = [*MultitenantModelWithMetadata.Meta.indexes, GinIndex(fields=["name", "slug"])]
