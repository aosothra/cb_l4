import json
import re
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument('path_to_txt', help='Path to txt file with questions')
    parser.add_argument('--path_to_json', default='quiz.json', help='Path to resulting JSON with questions')
    parser.add_argument('--encoding', '-e', default='koi8-r', help='Encoding of txt file with questions')
    parser.add_argument('--append', '-a', action='store_true', help='Add questions to JSON instead of rewriting it')
    args = parser.parse_args()

    quiz = {}

    if args.append:
        with open(args.path_to_json, mode='r', encoding='utf-8') as quiz_json:
            quiz = json.load(quiz_json)

    with open(args.path_to_txt, mode='r', encoding=args.encoding) as questions_txt:
        is_question_next = False
        is_answer_next = False
        question_lines = []
        
        for line in questions_txt.readlines():
            if ('Вопрос' in line) and (not is_question_next):
                is_question_next = True

            elif 'Ответ' in line:
                is_question_next = False
                is_answer_next = True

            elif is_question_next:
                question_lines.append(line.strip())

            elif is_answer_next:
                question = ' '.join(question_lines)
                answer = line.strip('\n .\t').lower()

                # Due to inconsistent format of answers save only
                # those questions which have single word answers 

                if re.match(r'^\w+\b$', answer):
                    quiz[question] = answer

                is_answer_next = False
                is_question_next = False

                question_lines.clear()

    with open(args.path_to_json, mode='w', encoding='utf-8') as quiz_json:
        json.dump(quiz, quiz_json, ensure_ascii=False)


if __name__ == '__main__':
    main()
