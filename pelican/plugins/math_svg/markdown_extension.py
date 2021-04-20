import re
from xml.etree import ElementTree

from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor

from .render import render_svg


class InlineMathProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        equation = m.group(1).strip()
        svg = render_svg(self.unescape(equation))
        element = ElementTree.Element("span")
        element.set("class", "math")
        element.text = self.md.htmlStash.store(svg)
        return element, m.start(0), m.end(0)


class DisplayMathProcessor(BlockProcessor):
    RE_START = re.compile(r"^\s*\$\$\s*\n")
    RE_END = re.compile(r"\n\s*\$\$\s*$")

    def test(self, parent, block):
        return self.RE_START.match(block)

    def run(self, parent, blocks):
        original_block = blocks[0]

        # remove starting fence
        blocks[0] = self.RE_START.sub("", blocks[0])

        for block_index, block in enumerate(blocks):
            if self.RE_END.search(block):
                # remove ending fence
                stripped_block = self.RE_END.sub("", block)
                blocks[block_index] = stripped_block

                element = ElementTree.SubElement(parent, "div")
                element.set("class", "math")
                element.text = self.parser.md.htmlStash.store(
                    render_svg(stripped_block.strip())
                )
                # self.parser.parseBlocks(element, blocks[0 : block_index + 1])

                for i in range(0, block_index + 1):
                    blocks.pop(0)
                return True

        blocks[0] = original_block
        return False
