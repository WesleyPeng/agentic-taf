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

from taf.foundation.api.ui.patterns.basepattern import BasePattern
from taf.foundation.api.ui.patterns.invoke import Invoke
from taf.foundation.api.ui.patterns.toggle import Toggle
from taf.foundation.api.ui.patterns.value import Value
from taf.foundation.api.ui.patterns.text import Text
from taf.foundation.api.ui.patterns.selection import Selection
from taf.foundation.api.ui.patterns.selectionitem import SelectionItem
from taf.foundation.api.ui.patterns.container import Container
from taf.foundation.api.ui.patterns.expandcollapse import ExpandCollapse
from taf.foundation.api.ui.patterns.grid import Grid
from taf.foundation.api.ui.patterns.table import Table


class TestBasePattern(TestCase):
    """BasePattern is an empty base class for all UI patterns."""

    def test_instantiation(self):
        p = BasePattern()
        self.assertIsInstance(p, BasePattern)

    def test_no_abstract_methods(self):
        self.assertTrue(callable(BasePattern))


class TestInvokePattern(TestCase):

    def test_inherits_base_pattern(self):
        self.assertTrue(issubclass(Invoke, BasePattern))

    def test_click_raises(self):
        with self.assertRaises(NotImplementedError):
            Invoke().click()

    def test_enabled_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Invoke().enabled


class TestTogglePattern(TestCase):

    def test_inherits_base_pattern(self):
        self.assertTrue(issubclass(Toggle, BasePattern))

    def test_toggle_raises(self):
        with self.assertRaises(NotImplementedError):
            Toggle().toggle()

    def test_state_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Toggle().state


class TestValuePattern(TestCase):

    def test_inherits_base_pattern(self):
        self.assertTrue(issubclass(Value, BasePattern))

    def test_set_raises(self):
        with self.assertRaises(NotImplementedError):
            Value().set('x')

    def test_value_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Value().value

    def test_is_read_only_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Value().is_read_only


class TestTextPattern(TestCase):

    def test_inherits_base_pattern(self):
        self.assertTrue(issubclass(Text, BasePattern))

    def test_get_selection_raises(self):
        with self.assertRaises(NotImplementedError):
            Text().get_selection()

    def test_text_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Text().text

    def test_supports_text_selection_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Text().supports_text_selection


class TestSelectionPattern(TestCase):

    def test_inherits_base_pattern(self):
        self.assertTrue(issubclass(Selection, BasePattern))

    def test_can_select_multiple_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Selection().can_select_multiple

    def test_is_selection_required_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Selection().is_selection_required


class TestSelectionItemPattern(TestCase):

    def test_inherits_base_pattern(self):
        self.assertTrue(issubclass(SelectionItem, BasePattern))

    def test_select_raises(self):
        with self.assertRaises(NotImplementedError):
            SelectionItem().select()

    def test_deselect_raises(self):
        with self.assertRaises(NotImplementedError):
            SelectionItem().deselect()

    def test_is_selected_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = SelectionItem().is_selected


class TestContainerPattern(TestCase):

    def test_inherits_base_pattern(self):
        self.assertTrue(issubclass(Container, BasePattern))

    def test_items_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Container().items


class TestExpandCollapsePattern(TestCase):

    def test_inherits_base_pattern(self):
        self.assertTrue(issubclass(ExpandCollapse, BasePattern))

    def test_state_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = ExpandCollapse().state

    def test_expand_raises(self):
        with self.assertRaises(NotImplementedError):
            ExpandCollapse().expand()

    def test_collapse_raises(self):
        with self.assertRaises(NotImplementedError):
            ExpandCollapse().collapse()


class TestGridPattern(TestCase):

    def test_inherits_base_pattern(self):
        self.assertTrue(issubclass(Grid, BasePattern))

    def test_get_cell_raises(self):
        with self.assertRaises(NotImplementedError):
            Grid().get_cell(0, 0)

    def test_row_count_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Grid().row_count

    def test_column_count_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Grid().column_count


class TestTablePattern(TestCase):

    def test_inherits_grid(self):
        self.assertTrue(issubclass(Table, Grid))

    def test_header_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Table().header

    def test_foot_raises(self):
        with self.assertRaises(NotImplementedError):
            _ = Table().foot
