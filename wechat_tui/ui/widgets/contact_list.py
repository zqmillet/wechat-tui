"""Contact list widget for displaying WeChat contacts."""

from typing import Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Static

from ...models.contact import Contact, ContactType


class ContactItem(Static):
    """A single contact item in the list - clickable Static widget."""

    DEFAULT_CSS = """
    ContactItem {
        width: 100%;
        height: 3;
        padding: 1;
        margin: 0;
        background: #161b22;
        color: #c9d1d9;
    }

    ContactItem:hover {
        background: #21262d;
        color: #ffffff;
    }

    ContactItem.selected {
        background: #1f6feb;
        color: #ffffff;
    }
    """

    class Selected(Message):
        """Sent when a contact is selected."""

        def __init__(self, contact: Contact) -> None:
            self.contact = contact
            super().__init__()

    def __init__(self, contact: Contact) -> None:
        # Build label - use simple prefix
        prefix = "[群]" if contact.is_chatroom else "[友]"
        if contact.contact_type == ContactType.MP:
            prefix = "[公]"
        name = contact.display_name
        if len(name) > 16:
            name = name[:13] + "..."
        if contact.unread_count > 0:
            label_text = f"{prefix} {name} [{contact.unread_count}]"
        else:
            label_text = f"{prefix} {name}"
        # Pass content to Static
        super().__init__(label_text)
        self._contact = contact
        self._selected = False

    def on_click(self) -> None:
        """Handle click event."""
        self.post_message(self.Selected(self._contact))

    def set_selected(self, selected: bool) -> None:
        """Set selection state."""
        self._selected = selected
        self.set_class(selected, "selected")


class ContactList(Widget):
    """A scrollable list of contacts - WeChat style."""

    DEFAULT_CSS = """
    ContactList {
        width: 100%;
        height: 100%;
        background: #161b22;
    }

    ContactList Input {
        width: 100%;
        height: 1;
        min-height: 1;
        max-height: 1;
        background: #0d1117;
        border: none;
        padding: 0;
        color: #c9d1d9;
    }

    ContactList ScrollableContainer {
        height: 1fr;
    }

    ContactList .no-contacts {
        padding: 1;
        color: #8b949e;
        text-align: center;
    }
    """

    contacts: reactive[list[Contact]] = reactive(list)
    selected_contact: reactive[Optional[Contact]] = reactive(None)
    _all_contacts: list[Contact] = []
    _search_query: str = ""

    class ContactSelected(Message):
        """Sent when a contact is selected."""

        def __init__(self, contact: Contact) -> None:
            self.contact = contact
            super().__init__()

    def __init__(self, *, id: Optional[str] = None, classes: Optional[str] = None) -> None:
        super().__init__(id=id, classes=classes)
        self._contact_items: dict[str, ContactItem] = {}

    def compose(self) -> ComposeResult:
        """Compose the contact list with search."""
        yield Input(placeholder="🔍 搜索", id="contact-search")
        yield ScrollableContainer(Static("加载中...", classes="no-contacts"), id="contact-container")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "contact-search":
            self._search_query = event.value.lower()
            self._refresh_contacts()

    def watch_contacts(self, contacts: list[Contact]) -> None:
        """Store contacts and refresh display."""
        self._all_contacts = contacts
        self._refresh_contacts()

    def _refresh_contacts(self) -> None:
        """Refresh the contact list display."""
        try:
            container = self.query_one("#contact-container", ScrollableContainer)
        except Exception:
            return

        # Remove old items
        container.remove_children()

        # Filter contacts
        if self._search_query:
            filtered = [
                c for c in self._all_contacts
                if self._search_query in c.name.lower() or
                   self._search_query in c.display_name.lower()
            ]
        else:
            filtered = self._all_contacts

        if not filtered:
            msg = "无匹配" if self._search_query else "暂无联系人"
            container.mount(Static(msg, classes="no-contacts"))
            return

        # Add contact items
        self._contact_items.clear()
        for contact in filtered:
            item = ContactItem(contact)
            if self.selected_contact and contact.user_id == self.selected_contact.user_id:
                item.set_selected(True)
            self._contact_items[contact.user_id] = item
            container.mount(item)

    def update_contact(self, contact: Contact) -> None:
        """Update a single contact in the list."""
        if contact.user_id in self._contact_items:
            self._contact_items[contact.user_id].contact = contact

    def select_contact(self, contact: Contact) -> None:
        """Select a contact in the list."""
        # Deselect previous
        if self.selected_contact and self.selected_contact.user_id in self._contact_items:
            self._contact_items[self.selected_contact.user_id].set_selected(False)

        # Select new
        self.selected_contact = contact
        if contact.user_id in self._contact_items:
            self._contact_items[contact.user_id].set_selected(True)

    def on_contact_item_selected(self, event: ContactItem.Selected) -> None:
        """Handle contact selection."""
        self.select_contact(event.contact)
        self.post_message(self.ContactSelected(event.contact))