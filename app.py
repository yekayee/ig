from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    SelectContactPointRecoveryForm, RecaptchaChallengeForm,
    FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        credentials = request.form['credentials']
        url_post = request.form['url_post']
        comment_texts = request.form['comment_texts'].split('\n')  # Assuming comment_texts is a newline-separated input
        comment_file = request.form['comment_file']

        results = []
        accounts = credentials.split('\n')
        for i, account in enumerate(accounts):
            if '|' not in account:
                continue
            username, password = account.strip().split('|')
            
            session_dir = './tmp/session/'
            if not os.path.exists(session_dir):
                os.makedirs(session_dir)
            session_file = f'{session_dir}/{username}.json'

            if not os.path.exists(session_file):
                try:
                    client = Client()
                    client.delay_range = [1, 5]
                    client.login(username, password)
                    client.dump_settings(session_file)
                    login_status = 'Logged in successfully without sessions'
                except BadPassword:
                    login_status = 'Login failed - Bad password.'
                except ReloginAttemptExceeded:
                    login_status = 'Login failed - Relogin attempt exceeded.'
                except ChallengeRequired:
                    login_status = 'Login failed - Challenge required.'
                except SelectContactPointRecoveryForm:
                    login_status = 'Login failed - Contact point recovery required.'
                except RecaptchaChallengeForm:
                    login_status = 'Login failed - Recaptcha challenge required.'
                except FeedbackRequired:
                    login_status = 'Login failed - Feedback required.'
                except PleaseWaitFewMinutes:
                    login_status = 'Login failed - Please wait a few minutes before trying again.'
                except LoginRequired:
                    login_status = 'Login failed - Login required.'
                except Exception as e:
                    login_status = f'Login failed - {str(e)}'
            else:
                try:
                    client = Client()
                    client.delay_range = [1, 5]
                    client.load_settings(session_file)
                    client.login(username, password)
                    login_status = 'Logged in successfully using session'
                except BadPassword:
                    login_status = 'Login failed - Bad password.'
                except ReloginAttemptExceeded:
                    login_status = 'Login failed - Relogin attempt exceeded.'
                except ChallengeRequired:
                    login_status = 'Login failed - Challenge required.'
                except SelectContactPointRecoveryForm:
                    login_status = 'Login failed - Contact point recovery required.'
                except RecaptchaChallengeForm:
                    login_status = 'Login failed - Recaptcha challenge required.'
                except FeedbackRequired:
                    login_status = 'Login failed - Feedback required.'
                except PleaseWaitFewMinutes:
                    login_status = 'Login failed - Please wait a few minutes before trying again.'
                except LoginRequired:
                    login_status = 'Login failed - Login required.'
                except Exception as e:
                    login_status = f'Login failed - {str(e)}'

            # Comment logic
            if 'successfully' in login_status.lower():
                try:
                    media_id = client.media_id(client.media_pk_from_url(url_post))
                    # Ensure each account has a corresponding comment text
                    comment_text = comment_texts[i] if i < len(comment_texts) else "Default comment"
                    comment = client.media_comment(media_id, comment_text)
# Define the directory for storing comment files
                    comment_dir = os.path.join(os.getcwd(), '/tmp/data')
                    if not os.path.exists(comment_dir):
                        os.makedirs(comment_dir)

                    # Later in your code, when writing to the file
                    comment_file_path = os.path.join(comment_dir, comment_file)
                    with open(comment_file_path, 'a') as akun_file:
                        akun_file.write(url_post + 'c/' + str(comment.dict()['pk']) + '\n')
                    comment_status = 'Comment success'
                    comment_id = comment.dict()['pk']
                except Exception as e:
                    comment_status = f'Failed: {str(e)}'
                    comment_id = 'N/A'
            else:
                comment_status = 'No comment attempted'
                comment_id = 'N/A'

            results.append({
                'no': i + 1,
                'username': username,
                'status_login': login_status,
                'status_comment': comment_status,
                'comment_id': comment_id
            })

        return jsonify(results=results, comment_file=comment_file)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    directory = os.path.join(os.getcwd(), '/tmp/data')
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    try:
        return send_from_directory(directory=directory, filename=filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
