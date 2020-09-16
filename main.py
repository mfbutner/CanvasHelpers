import argparse
import canvasapi
from src.kudo_points.giving_quiz_creator.runner import create_assignment_group


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='Canvas Tool Helper',
                                     description='A collection of useful tools for interacting with Canvas',
                                     fromfile_prefix_chars='$')
    parser.add_argument('--key',
                        dest='canvas_key',
                        metavar='key',
                        required=True,
                        help="Your Canavs Access Token. "
                             "If you don't have one you can get one by following "
                             "directions under Manual Token Generation at "
                             "https://canvas.instructure.com/doc/api/file.oauth.html#accessing-canvas-api")
    parser.add_argument('--course_id',
                        dest='course_id',
                        required=True,
                        type=int,
                        help='The id of your course. You can find this right after /courses in the url '
                             'of your course.\n '
                             'For example, if the url of your course was https://canvas.ucdavis.edu/courses/1234 '
                             'then your course id is 1234.')

    parser.add_argument('--url', '--canvas_url',
                        dest='canvas_url',
                        default='https://canvas.ucdavis.edu/',
                        help='Your canvas url. Example: https://canvas.ucdavis.edu/'
                        )


    return parser


if __name__ == '__main__':
    # runner()
    p = create_argument_parser()
    n = p.parse_args()
    canvas_connection = canvasapi.Canvas(n.canvas_url, n.canvas_key)
    course = canvas_connection.get_course(n.course_id)
    create_assignment_group('Sparta', course,True)
