# Copyright (c) 2017-2026 Wesley Peng
#
# Licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0).
# You may obtain a copy of the License at
#
# https://www.gnu.org/licenses/lgpl-3.0.html
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

from unittest import TestCase

from taf.foundation.api.ui.patterns.invoke import Invoke
from taf.foundation.api.ui.patterns.toggle import Toggle
from taf.foundation.api.ui.patterns.value import Value
from taf.foundation.api.ui.patterns.text import Text
from taf.foundation.api.ui.patterns.selectionitem import SelectionItem
from taf.foundation.api.ui.patterns.container import Container
from taf.foundation.api.ui.patterns.expandcollapse import ExpandCollapse
from taf.foundation.api.ui.patterns.selection import Selection
from taf.foundation.api.ui.patterns.grid import Grid
from taf.foundation.api.ui.patterns.table import Table

from taf.foundation.api.ui.controls.button import Button
from taf.foundation.api.ui.controls.checkbox import CheckBox
from taf.foundation.api.ui.controls.edit import Edit
from taf.foundation.api.ui.controls.link import Link
from taf.foundation.api.ui.controls.text import Text as TextControl
from taf.foundation.api.ui.controls.listitem import ListItem
from taf.foundation.api.ui.controls.combobox import ComboBox
from taf.foundation.api.ui.controls.radiogroup import RadioGroup
from taf.foundation.api.ui.controls.frame import Frame
from taf.foundation.api.ui.controls.table import Table as TableControl


class TestButton(TestCase):
    """Button inherits from IInvoke (Invoke pattern)."""

    def test_inherits_invoke(self):
        self.assertTrue(issubclass(Button, Invoke))

    def test_click_raises(self):
        with self.assertRaises(NotImplementedError):
            Button().click()

    def test_enabled_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Button().enabled


class TestCheckBox(TestCase):
    """CheckBox inherits from IToggle (Toggle pattern) with tick/untick."""

    def test_inherits_toggle(self):
        self.assertTrue(issubclass(CheckBox, Toggle))

    def test_tick_raises(self):
        with self.assertRaises(NotImplementedError):
            CheckBox().tick()

    def test_untick_raises(self):
        with self.assertRaises(NotImplementedError):
            CheckBox().untick()

    def test_toggle_raises(self):
        with self.assertRaises(NotImplementedError):
            CheckBox().toggle()

    def test_state_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = CheckBox().state


class TestEdit(TestCase):
    """Edit inherits from IText and IValue."""

    def test_inherits_text(self):
        self.assertTrue(issubclass(Edit, Text))

    def test_inherits_value(self):
        self.assertTrue(issubclass(Edit, Value))

    def test_set_raises(self):
        with self.assertRaises(NotImplementedError):
            Edit().set('val')

    def test_value_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Edit().value


class TestLink(TestCase):
    """Link inherits from IInvoke and IText."""

    def test_inherits_invoke(self):
        self.assertTrue(issubclass(Link, Invoke))

    def test_inherits_text(self):
        self.assertTrue(issubclass(Link, Text))

    def test_click_raises(self):
        with self.assertRaises(NotImplementedError):
            Link().click()

    def test_text_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Link().text


class TestTextControl(TestCase):
    """Text control inherits from IText."""

    def test_inherits_text(self):
        self.assertTrue(issubclass(TextControl, Text))

    def test_text_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = TextControl().text


class TestListItem(TestCase):
    """ListItem inherits from ISelectionItem."""

    def test_inherits_selection_item(self):
        self.assertTrue(issubclass(ListItem, SelectionItem))

    def test_select_raises(self):
        with self.assertRaises(NotImplementedError):
            ListItem().select()

    def test_deselect_raises(self):
        with self.assertRaises(NotImplementedError):
            ListItem().deselect()

    def test_is_selected_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = ListItem().is_selected


class TestComboBox(TestCase):
    """ComboBox inherits from IExpandCollapse, IValue, ISelection."""

    def test_inherits_expandcollapse(self):
        self.assertTrue(issubclass(ComboBox, ExpandCollapse))

    def test_inherits_value(self):
        self.assertTrue(issubclass(ComboBox, Value))

    def test_inherits_selection(self):
        self.assertTrue(issubclass(ComboBox, Selection))

    def test_expand_raises(self):
        with self.assertRaises(NotImplementedError):
            ComboBox().expand()

    def test_options_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = ComboBox().options


class TestRadioGroup(TestCase):
    """RadioGroup inherits from IValue and IContainer."""

    def test_inherits_value(self):
        self.assertTrue(issubclass(RadioGroup, Value))

    def test_inherits_container(self):
        self.assertTrue(issubclass(RadioGroup, Container))

    def test_items_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = RadioGroup().items


class TestFrame(TestCase):
    """Frame inherits from IContainer."""

    def test_inherits_container(self):
        self.assertTrue(issubclass(Frame, Container))

    def test_items_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Frame().items


class TestTableControl(TestCase):
    """Table control inherits from ITable (Table pattern)."""

    def test_inherits_table_pattern(self):
        self.assertTrue(issubclass(TableControl, Table))

    def test_inherits_grid(self):
        self.assertTrue(issubclass(TableControl, Grid))

    def test_get_cell_raises(self):
        with self.assertRaises(NotImplementedError):
            TableControl().get_cell(0, 0)

    def test_header_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = TableControl().header
