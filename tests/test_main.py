import unittest
import os
from main import parse_feedback


class TestParser(unittest.TestCase):
    def test_parse_cs19(self):
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/sample_cs19.html") as f:
            body = f.read()
            res = parse_feedback(body, "1234abcdef")

        self.assertEqual(res['raw_data'], body)
        self.assertEqual(res['title'], 'feedback for quiz-cs_20191030')
        self.assertEqual(res['submit_date'], '2019/11/11 14:55:39')
        self.assertEqual(res['score_count'], {
                         0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0, 10: 50})
        self.assertEqual(res['ans'], [
            {
                "qname": "q1a",
                "res": "True",
                "your_ans": "26",
                "ans": "['26']"
            },
            {
                "qname": "q1b",
                "res": "True",
                "your_ans": "2",
                "ans": "['2']"
            },
            {
                "qname": "q1c",
                "res": "True",
                "your_ans": "4",
                "ans": "['4']"
            },
            {
                "qname": "q1d",
                "res": "True",
                "your_ans": "mhmhmmhhmhhh",
                "ans": "['mhmhmmhhmhhh']"
            },
        ],
        )
        self.assertEqual(res['stats'], [
            {
                "qname": "q1a",
                "rate": 10.9,
                "pos": 10,
                "N": 57
            },
            {
                "qname": "q1b",
                "rate": 21.8,
                "pos": 20,
                "N": 57
            },
            {
                "qname": "q1c",
                "rate": 32.7,
                "pos": 30,
                "N": 57
            },
            {
                "qname": "q1d",
                "rate": 43.6,
                "pos": 40,
                "N": 57
            }
        ])

    def test_parse_no_match(self):
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/sample_no_match.html") as f:
            body = f.read()
            res = parse_feedback(body, "1234abcdef")

        self.assertEqual(res['title'], 'feedback for quiz-20191007')
        self.assertEqual(res['error'], True)
        self.assertEqual(res['score_count'], {0: 10, 1: 11, 2: 12})
        self.assertEqual(res['ans'], [])
        self.assertEqual(res['stats'], [
            {
                "qname": "q3a",
                "rate": 50.5,
                "pos": 100,
                "N": 129
            },
            {
                "qname": "q3b",
                "rate": 10.3,
                "pos": 60,
                "N": 129
            },
            {
                "qname": "q3c",
                "rate": 90.1,
                "pos": 120,
                "N": 129
            }
        ])


if __name__ == '__main__':
    unittest.main()
