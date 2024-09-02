from unittest import mock

from gui.indexcombobox import IndexCombobox


class TestIndexComboBox:
    options = [
        "an option",
        "another option",
        "yet another option",
    ]

    def test_sets_defaults(self, qtbot):
        index_combobox = IndexCombobox(
            self.options,
            setter := mock.Mock(),
            label_text="X Column",
            default_index=2,
        )
        qtbot.addWidget(index_combobox)

        assert index_combobox.currentIndex() == 2
        assert index_combobox.items() == self.options
        setter.assert_called_once_with(2)

    def test_changes_mapping_when_changing_columns(self, qtbot):
        index_combobox = IndexCombobox(
            self.options,
            setter := mock.Mock(),
            label_text="X Column",
        )
        qtbot.addWidget(index_combobox)

        index_combobox.setCurrentIndex(1)

        setter.assert_called_with(1)
