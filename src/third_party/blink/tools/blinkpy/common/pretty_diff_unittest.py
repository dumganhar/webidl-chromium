class TestFileDiff(unittest.TestCase):
        lines = [
            'diff --git a/platform/modules/offscreencanvas/OWNERS b/platform/modules/frame_sinks/OWNERS',
            'similarity index 100%',
            'rename from platform/modules/offscreencanvas/OWNERS',
            'rename to platform/modules/frame_sinks/OWNERS',
            'diff --git a/mojom/frame_sinks/embedded_frame_sink.mojom ' +
            'b/mojom/frame_sinks/embedded_frame_sink.mojom'
        ]
        lines = [
            'diff --git a/third_party/blink/text-to-zero.txt b/third_party/blink/text-to-zero.txt',
            'index 2262de0..e69de29 100644',
            '--- a/third_party/blink/text-to-zero.txt',
            '+++ b/third_party/blink/text-to-zero.txt', '@@ -1 +0,0 @@',
            '-hoge'
        ]
        lines = [
            'diff --git a/text-to-be-removed.txt b/text-to-be-removed.txt',
            'deleted file mode 100644', 'index 2262de0..0000000',
            '--- a/text-to-be-removed.txt', '+++ /dev/null', '@@ -1 +0,0 @@',
            '-hoge'
        ]
        lines = [
            'diff --git a/text-zero.txt b/text-zero.txt',
            'deleted file mode 100644', 'index e69de29..0000000'
        ]
        lines = [
            'diff --git a/text-zero.txt b/text-zero.txt',
            'new file mode 100644', 'index 0000000..e69de29'
        ]
        lines = [
            'diff --git a/binary-to-zero.png b/binary-to-zero.png',
            'index 9b56f1c6942441578b0585d8b9688fdfcb2aa3fd..e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 100644',
            'GIT binary patch', 'literal 0', 'HcmV?d00001', '', 'literal 6',
            'NcmZSh&&2%iKL7{~0|Ed5', ''
        ]
        lines = [
            'diff --git a/binary-to-be-removed.png b/binary-to-be-removed.png',
            'deleted file mode 100644',
            'index 9b56f1c6942441578b0585d8b9688fdfcb2aa3fd..0000000000000000000000000000000000000000',
            'GIT binary patch', 'literal 0', 'HcmV?d00001', '', 'literal 6',
            'NcmZSh&&2%iKL7{~0|Ed5', ''
        ]
        lines = [
            'diff --git a/binary-to-zero.png b/binary-to-zero.png',
            'new file mode 100644',
            'index 0000000000000000000000000000000000000000..9b56f1c6942441578b0585d8b9688fdfcb2aa3fd',
            'GIT binary patch', 'literal 6', 'NcmZSh&&2%iKL7{~0|Ed5', '',
            'literal 0', 'HcmV?d00001', ''
        ]
        self.assertEquals(
            DiffHunk._find_operations(['-', '-']), [([0, 1], [])])
        self.assertEquals(
            DiffHunk._find_operations([' ', '-', '-']), [([1, 2], [])])
        self.assertEquals(
            DiffHunk._find_operations(['-', '-', ' ']), [([0, 1], [])])
        self.assertEquals(
            DiffHunk._find_operations(['+', '+']), [([], [0, 1])])
        self.assertEquals(
            DiffHunk._find_operations([' ', '+', '+']), [([], [1, 2])])
        self.assertEquals(
            DiffHunk._find_operations(['+', '+', ' ']), [([], [0, 1])])
        self.assertEquals(
            DiffHunk._find_operations(['-', '-', '+', '+']),
            [([0, 1], [2, 3])])
        self.assertEquals(
            DiffHunk._find_operations([' ', '-', '-', '+']), [([1, 2], [3])])
        self.assertEquals(
            DiffHunk._find_operations(['-', '-', '+', '+', ' ']),
            [([0, 1], [2, 3])])
        self.assertEquals(
            DiffHunk._find_operations(['-', '-', '+', '+', '-']),
            [([0, 1], [2, 3]), ([4], [])])
        self.assertEquals(
            DiffHunk._find_operations(['-', '+', '-', '+']), [([0], [1]),
                                                              ([2], [3])])
        self.assertEquals(self._annotate(['-abcdef'], 0, 2, 4), [[(2, 4)]])
        self.assertEquals(
            self._annotate(['-abcdef', '-ghi'], 0, 2, 6), [[(2, 6)], None])
        self.assertEquals(
            self._annotate(['-abcdef', '-ghi'], 0, 2, 7), [[(2, 6)], [(0, 1)]])
        self.assertEquals(
            self._annotate(['-abcdef', '-ghi', '-jkl'], 0, 2, 11),
            [[(2, 6)], [(0, 3)], [(0, 2)]])
        self.assertEquals(
            self._annotate(['+', '+abc', ' de'], 0, 0, 2),
            [[(0, 0)], [(0, 2)], None])
        self.assertTrue(
            'data:image/png;base64,' in binary.prettify('image/png', 'add'))
        self.assertTrue(
            '<img ' not in binary.prettify('application/octet-stream', 'del'))