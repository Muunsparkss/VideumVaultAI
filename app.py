from flask import Flask, request, jsonify, send_from_directory ,render_template
import yt_dlp
import os
import threading
import time
import google.generativeai as genai
from googleapiclient.discovery import build
youtube = build('youtube', 'v3', developerKey="YOUR-YOUTUBE-API-KEY")
genai.configure(api_key="YOUR-GEMINI-API-KEY")

model = genai.GenerativeModel('gemini-1.0-pro-latest')

app = Flask(__name__)
download_folder = 'downloads'
os.makedirs(download_folder, exist_ok=True)
downloads = {}  # To keep track of the download status

def get_video_details(video_id):
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()

    # Extract title and description
    title = response['items'][0]['snippet']['title']
    description = response['items'][0]['snippet']['description']

    return title, description

def download_video(url, video_id):
    video_path = os.path.join(download_folder, f"{video_id}.mp4")
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': video_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    downloads[video_id] = 'ready'  # Mark as ready

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        video_id = url.split('v=')[-1]
        video_path = os.path.join(download_folder, f"{video_id}.mp4")

        if not os.path.exists(video_path):
            if video_id not in downloads:
                downloads[video_id] = 'waiting'  # Mark as waiting
                thread = threading.Thread(target=download_video, args=(url, video_id))
                thread.start()
            return jsonify({'status': 'waiting', 'video_id': video_id})

        return jsonify({'status': 'ready', 'video_id': video_id})

    return '''
    <!doctype html>
    <html>
    <head>
        <title>Videum Vault AI || Youtube Downloader</title>
        <style>
            body {  
                    padding:0;
                    font-family: Arial, sans-serif;
                    background: linear-gradient(45deg, #021526, #03346E, #6EACDA);
                    background-size: 600% 600%;
                    animation: gradient 15s ease infinite;
                    text-align: center;
                    color: white;
                    height: 100vh;
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    }

            @keyframes gradient {
                0% { background-position: 0% 0%; }
                50% { background-position: 100% 100%; }
                100% { background-position: 0% 0%; }
            }
            .container {
                max-width: 500px;
                width: 100%;
                padding: 20px;
                border-radius: 10px;
                background-color: rgba(0, 0, 0, 0.6);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                margin-bottom: 60px; /* Space for footer */
            }
            .logo {
                margin-bottom: 20px;
            }
            .logo img {
                max-width: 200px; /* Adjust as needed */
                height: auto;
            }
            input[type="text"] {
                width: calc(100% - 22px);
                padding: 10px;
                margin-bottom: 10px;
                border: none;
                border-radius: 5px;
            }
            button {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                background-color: #f06595;
                color: white;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #ff6b6b;
            }
            #status {
                margin-top: 20px;
            }
            footer {
                position:relative;
                bottom: 0;
                width: 100%;
                background-color: rgba(0, 0, 0, 0.6);
                color: white;
                padding: 10px 0;
                text-align: center;
                font-size: 14px;
            }
                nav {
                  top: 0;
                  left: 0;
                  width: 100%;
                  padding: 0px;
                  display: flex;
                  align-items: center;
                  transition: 0.3s ease-out;
                  backdrop-filter: blur(8px) brightness(1.2);
                  -webkit-backdrop-filter: blur(8px) brightness(1.2);
                  text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
                  color: white;
                  font-size: 16px;
                  &.mask {
                    top: 0px;
                    mask-image: linear-gradient(black 70%, transparent);
                    -webkit-mask-image: linear-gradient(black 70%, transparent);
                  }
                  &.mask-pattern {
                    top: 300px;
                    mask-image: url("data:image/svg+xml, %3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 12.21 10.57%27%3E%3Cpath fill=%27%23ffffff%27 d=%27M6.1 0h6.11L9.16 5.29 6.1 10.57 3.05 5.29 0 0h6.1z%27/%3E%3C/svg%3E"),
                      linear-gradient(black calc(100% - 30px), transparent calc(100% - 30px));
                    mask-size: auto 30px, 100% 100%;
                    mask-repeat: repeat-x, no-repeat;
                    mask-position: left bottom, top left;

                    -webkit-mask-image: url("data:image/svg+xml, %3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 12.21 10.57%27%3E%3Cpath fill=%27%23ffffff%27 d=%27M6.1 0h6.11L9.16 5.29 6.1 10.57 3.05 5.29 0 0h6.1z%27/%3E%3C/svg%3E"),
                      linear-gradient(black calc(100% - 30px), transparent calc(100% - 30px));
                    -webkit-mask-size: auto 30px, 100% 100%;
                    -webkit-mask-repeat: repeat-x, no-repeat;
                    -webkit-mask-position: left bottom, top left;
                  }

                  @media (min-width: 640px) {
                    padding: 16px 50px 30px 50px;
                  }
                }
                nav.is-hidden {
                  transform: translateY(-100%);
                }
                a {
                  color: inherit;
                  text-decoration: none;
                  &:hover,
                  &:focus {
                    text-decoration: underline;
                  }
                }
                .list {
                  width:70%;
                  justify-content:center;
                  align-items:center;
                  list-style-type: none;
                  margin-left: 0;
                  display: none;
                  @media (min-width: 640px) {
                    display: flex;
                  }
                  li {
                    margin-left: 20px;
                  }
                }
                .search {
                  display: inline-block;
                  padding: 0;
                  font-size: 0;
                  background: none;
                  border: none;
                  margin-left: auto;
                  filter: drop-shadow(0 0 5px rgba(0, 0, 0, 0.5));
                  @media (min-width: 640px) {
                    margin-left: 20px;
                  }

                  &::before {
                    content: "";
                    display: inline-block;
                    width: 2rem;
                    height: 2rem;
                    background: center/1.3rem 1.3rem no-repeat
                      url("data:image/svg+xml, %3Csvg%20xmlns=%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox=%270%200%2015.17%2014.81%27%20width=%2715.17%27%20height=%2714.81%27%3E%3Cpath%20d=%27M6,.67A5.34,5.34,0,1,1,.67,6,5.33,5.33,0,0,1,6,.67ZM9.86,9.58l4.85,4.75Z%27%20fill=%27none%27%20stroke=%27%23fff%27%20stroke-width=%271.33%27%2F%3E%3C%2Fsvg%3E");
                  }
                }
                .menu {
                  display: inline-block;
                  padding: 0;
                  font-size: 0;
                  background: none;
                  border: none;
                  margin-left: 20px;
                  filter: drop-shadow(0 0 5px rgba(0, 0, 0, 0.5));
                  &::before {
                    content: url("data:image/svg+xml, %3Csvg%20xmlns=%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox=%270%200%2024.8%2018.92%27%20width=%2724.8%27%20height=%2718.92%27%3E%3Cpath%20d=%27M23.8,9.46H1m22.8,8.46H1M23.8,1H1%27%20fill=%27none%27%20stroke=%27%23fff%27%20stroke-linecap=%27round%27%20stroke-width=%272%27%2F%3E%3C%2Fsvg%3E");
                  }
                  @media (min-width: 640px) {
                    display: none;
                  }
                }
                .Title h1 {
                          text-align:center; font-size:50px; text-transform:uppercase; color:#c1f7cf; letter-spacing:1px;
                          font-family:"Playfair Display", serif; font-weight:400;
                    }
                .Title h1 span {
  margin-top: 5px;
    font-size:15px; color:#c1f7cf; word-spacing:1px; font-weight:normal; letter-spacing:2px;
    text-transform: uppercase; font-family:"Raleway", sans-serif; font-weight:500;

    display: grid;
    grid-template-columns: 1fr max-content 1fr;
    grid-template-rows: 27px 0;
    grid-gap: 20px;
    align-items: center;
}

.Title h1 span:after,.Title h1 span:before {
    content: " ";
    display: block;
    border-bottom: 1px solid #ccc;
    border-top: 1px solid #ccc;
    height: 5px;
  background-color:#f8f8f8;
}
.parag{
    margin-top:30px;
    width: 70%;
    align-self: center;
    justify-content: center;
    justify-items: center;
    align-items: center;
}
.parag h3 {
  text-align: center;
  font-size: 22px;
  font-weight: 700; color:#202020;
  text-transform: uppercase;
  word-spacing: 1px; letter-spacing:2px;
}

p{
    color:#f7f7f8;
}


        </style>
    </head>
    <body>
        <nav class="mask">
              <a href="#"><img src="./static/logo.png" style="width:100px;height:100px; margin-left:15px;"/></a>
              <ul class="list">
                <li><a href="/">Home</a></li>
                <li><a href="/analyze">Video Analyze</a></li>
                <li><a href="#">About Me</a></li>
                <li><a href="#">Contact</a></li>
              </ul>
              <button class="menu">Menu</button>
        </nav>
        <div class="Title">
            <h1>Welcome to Videum Vault AI <span>Download Videos From Youtube</span></h1>
        </div>
        <div class="container">
            <form id="download-form">
                <input type="text" id="url" name="url" placeholder="Enter YouTube URL" required>
                <button type="submit">Download</button>
            </form>
            <div id="status"></div>
        </div>
        <div class="parag">
            <h1>An Innovative Approach to Youtube Video Downlad
            </h1>
            <p>In today's fast-paced digital world, the need for quick, reliable, and efficient video downloading has never been greater. Whether you're saving a tutorial for offline viewing, archiving content for future reference, or simply building a personal media library, Videum Vault AI is here to make the process seamless.<br/><br/><br/>

Videum Vault AI represents the next generation of YouTube video downloading. We've reimagined the traditional downloader, infusing it with cutting-edge technology and a user-centric design, ensuring that every download is not only fast but also incredibly easy.
<h3 style="color:#f7f7f8;">Why Choose Videum Vault AI?</h3>
<ul>
<li>
Speed and Efficiency: Our platform is optimized to provide the fastest download speeds possible, ensuring that your videos are ready in no time.</li><br/><br/>

<li>User-Friendly Interface: With a clean, simple layout and intuitive controls, Videum Vault AI offers a stress-free experience for users of all technical levels.</li><br/><br/>

<li>Dynamic Backgrounds: Experience a visually appealing interface that features animated, colored backgrounds, adding a touch of style to your downloading process.

<li>Seamless Integration: No need to worry about complicated redirects or additional pages. Everything you need is on a single, streamlined page.</li><br/><br/>

<li>Smart Download Notifications: Our system will keep you informed about your download status in real time, eliminating the guesswork.</li><br/><br/><br/></ul>

<h3 style="color:#f7f7f8;">How It Works</h3>
<ol>
<li>Enter the URL: Simply paste the YouTube video URL into the provided field.</li><br/><br/>

<li>Download: Click the download button. If the video is ready for download, you'll get a direct link. If not, we'll handle the rest, and you'll be notified as soon as it's ready.</li><br/><br/>

<li>Enjoy: Download your video and enjoy it on any device, anytime, anywhere.</li><br/><br/></ol>

<h3 style="color:#f7f7f8;">Join the Revolution</h3><br/>
Experience the future of video downloading today with Videum Vault AI. Our innovative approach ensures that your favorite content is always just a click away.<br/>

Thank you for choosing Videum Vault AI – where simplicity meets innovation.
</p>
        </div>
        <footer>
            &copy; 2024 By Muunsparks to Society
        </footer>
        <script>
            document.getElementById('download-form').addEventListener('submit', function(event) {
                event.preventDefault();
                var url = document.getElementById('url').value;
                var formData = new FormData();
                formData.append('url', url);

                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/', true);
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                xhr.onload = function() {
                    if (xhr.status === 200) {
                        var response = JSON.parse(xhr.responseText);
                        var statusDiv = document.getElementById('status');
                        var button = document.querySelector('button');

                        if (response.status === 'waiting') {
                            button.style.display = 'none';
                            statusDiv.innerHTML = 'Please wait, your video is being processed...';
                            
                            // Check status periodically
                            var checkStatus = setInterval(function() {
                                var xhrStatus = new XMLHttpRequest();
                                xhrStatus.open('GET', '/' + response.video_id, true);
                                xhrStatus.onload = function() {
                                    if (xhrStatus.status === 200) {
                                        var statusResponse = JSON.parse(xhrStatus.responseText);
                                        if (statusResponse.status === 'ready') {
                                            clearInterval(checkStatus);
                                            statusDiv.innerHTML = '<a href="/downloads/' + response.video_id + '.mp4" download><button>READY</button></a>';
                                        }
                                    }
                                };
                                xhrStatus.send();
                            }, 2000); // Check every 2 seconds
                        } else if (response.status === 'ready') {
                            button.style.display = 'none';
                            statusDiv.innerHTML = '<a href="/downloads/' + response.video_id + '.mp4" download><button>READY</button></a>';
                        }
                    }
                };
                xhr.send(formData);
            });
        </script>
    </body>
    </html>
    '''

@app.route('/<video_id>')
def check_status(video_id):
    status = downloads.get(video_id, 'waiting')
    return jsonify({'status': status})

@app.route('/downloads/<filename>')
def download_file(filename):
    file_path = os.path.join(download_folder, filename)
    
    # Send the file for download
    response = send_from_directory(download_folder, filename)
    
    # After sending the file, delete it
    @response.call_on_close
    def remove_file():
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return response

@app.route('/analyze')
def analyze_page():
    return """    <!doctype html>
    <html>
    <head>
        <title>YouTube Downloader</title>
        <style>
            body {  
                    padding:0;
                    font-family: Arial, sans-serif;
                    background: linear-gradient(45deg, #021526, #03346E, #6EACDA);
                    background-size: 600% 600%;
                    animation: gradient 15s ease infinite;
                    text-align: center;
                    color: white;
                    height: 100vh;
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    }

            @keyframes gradient {
                0% { background-position: 0% 0%; }
                50% { background-position: 100% 100%; }
                100% { background-position: 0% 0%; }
            }
            .container {
                max-width: 500px;
                width: 100%;
                padding: 20px;
                border-radius: 10px;
                background-color: rgba(0, 0, 0, 0.6);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                margin-bottom: 60px; /* Space for footer */
            }
            .logo {
                margin-bottom: 20px;
            }
            .logo img {
                max-width: 200px; /* Adjust as needed */
                height: auto;
            }
            input[type="text"] {
                width: calc(100% - 22px);
                padding: 10px;
                margin-bottom: 10px;
                border: none;
                border-radius: 5px;
            }
            button {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                background-color: #f06595;
                color: white;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #ff6b6b;
            }
            #status {
                margin-top: 20px;
            }
            footer {
                position:relative;
                bottom: 0;
                width: 100%;
                background-color: rgba(0, 0, 0, 0.6);
                color: white;
                padding: 10px 0;
                text-align: center;
                font-size: 14px;
            }
                nav {
                  top: 0;
                  left: 0;
                  width: 100%;
                  padding: 0px;
                  display: flex;
                  align-items: center;
                  transition: 0.3s ease-out;
                  backdrop-filter: blur(8px) brightness(1.2);
                  -webkit-backdrop-filter: blur(8px) brightness(1.2);
                  text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
                  color: white;
                  font-size: 16px;
                  &.mask {
                    top: 0px;
                    mask-image: linear-gradient(black 70%, transparent);
                    -webkit-mask-image: linear-gradient(black 70%, transparent);
                  }
                  &.mask-pattern {
                    top: 300px;
                    mask-image: url("data:image/svg+xml, %3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 12.21 10.57%27%3E%3Cpath fill=%27%23ffffff%27 d=%27M6.1 0h6.11L9.16 5.29 6.1 10.57 3.05 5.29 0 0h6.1z%27/%3E%3C/svg%3E"),
                      linear-gradient(black calc(100% - 30px), transparent calc(100% - 30px));
                    mask-size: auto 30px, 100% 100%;
                    mask-repeat: repeat-x, no-repeat;
                    mask-position: left bottom, top left;

                    -webkit-mask-image: url("data:image/svg+xml, %3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 12.21 10.57%27%3E%3Cpath fill=%27%23ffffff%27 d=%27M6.1 0h6.11L9.16 5.29 6.1 10.57 3.05 5.29 0 0h6.1z%27/%3E%3C/svg%3E"),
                      linear-gradient(black calc(100% - 30px), transparent calc(100% - 30px));
                    -webkit-mask-size: auto 30px, 100% 100%;
                    -webkit-mask-repeat: repeat-x, no-repeat;
                    -webkit-mask-position: left bottom, top left;
                  }

                  @media (min-width: 640px) {
                    padding: 16px 50px 30px 50px;
                  }
                }
                nav.is-hidden {
                  transform: translateY(-100%);
                }
                a {
                  color: inherit;
                  text-decoration: none;
                  &:hover,
                  &:focus {
                    text-decoration: underline;
                  }
                }
                .list {
                  width:70%;
                  justify-content:center;
                  align-items:center;
                  list-style-type: none;
                  margin-left: 0;
                  display: none;
                  @media (min-width: 640px) {
                    display: flex;
                  }
                  li {
                    margin-left: 20px;
                  }
                }
                .search {
                  display: inline-block;
                  padding: 0;
                  font-size: 0;
                  background: none;
                  border: none;
                  margin-left: auto;
                  filter: drop-shadow(0 0 5px rgba(0, 0, 0, 0.5));
                  @media (min-width: 640px) {
                    margin-left: 20px;
                  }

                  &::before {
                    content: "";
                    display: inline-block;
                    width: 2rem;
                    height: 2rem;
                    background: center/1.3rem 1.3rem no-repeat
                      url("data:image/svg+xml, %3Csvg%20xmlns=%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox=%270%200%2015.17%2014.81%27%20width=%2715.17%27%20height=%2714.81%27%3E%3Cpath%20d=%27M6,.67A5.34,5.34,0,1,1,.67,6,5.33,5.33,0,0,1,6,.67ZM9.86,9.58l4.85,4.75Z%27%20fill=%27none%27%20stroke=%27%23fff%27%20stroke-width=%271.33%27%2F%3E%3C%2Fsvg%3E");
                  }
                }
                .menu {
                  display: inline-block;
                  padding: 0;
                  font-size: 0;
                  background: none;
                  border: none;
                  margin-left: 20px;
                  filter: drop-shadow(0 0 5px rgba(0, 0, 0, 0.5));
                  &::before {
                    content: url("data:image/svg+xml, %3Csvg%20xmlns=%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox=%270%200%2024.8%2018.92%27%20width=%2724.8%27%20height=%2718.92%27%3E%3Cpath%20d=%27M23.8,9.46H1m22.8,8.46H1M23.8,1H1%27%20fill=%27none%27%20stroke=%27%23fff%27%20stroke-linecap=%27round%27%20stroke-width=%272%27%2F%3E%3C%2Fsvg%3E");
                  }
                  @media (min-width: 640px) {
                    display: none;
                  }
                }
                .Title h1 {
                          text-align:center; font-size:50px; text-transform:uppercase; color:#c1f7cf; letter-spacing:1px;
                          font-family:"Playfair Display", serif; font-weight:400;
                    }
                .Title h1 span {
  margin-top: 5px;
    font-size:15px; color:#c1f7cf; word-spacing:1px; font-weight:normal; letter-spacing:2px;
    text-transform: uppercase; font-family:"Raleway", sans-serif; font-weight:500;

    display: grid;
    grid-template-columns: 1fr max-content 1fr;
    grid-template-rows: 27px 0;
    grid-gap: 20px;
    align-items: center;
}

.Title h1 span:after,.Title h1 span:before {
    content: " ";
    display: block;
    border-bottom: 1px solid #ccc;
    border-top: 1px solid #ccc;
    height: 5px;
  background-color:#f8f8f8;
}
.parag{
    margin-top:30px;
    width: 70%;
    align-self: center;
    justify-content: center;
    justify-items: center;
    align-items: center;
}
.parag h3 {
  text-align: center;
  font-size: 22px;
  font-weight: 700; color:#202020;
  text-transform: uppercase;
  word-spacing: 1px; letter-spacing:2px;
}

p{
    color:#f7f7f8;
}


        </style>
    </head>
    <body>
        <nav class="mask">
              <a href="#"><img src="./static/logo.png" style="width:100px;height:100px; margin-left:15px;"/></a>
              <ul class="list">
                <li><a href="/">Home</a></li>
                <li><a href="/analyze">Video Analyze</a></li>
                <li><a href="#">About Me</a></li>
                <li><a href="#">Contact</a></li>
              </ul>
              <button class="menu">Menu</button>
        </nav>
        <div class="Title">
            <h1>Welcome to Videum Vault AI <span>Download Videos From Youtube</span></h1>
        </div>
        <div class="container">
            <h2>Analyze YouTube Video</h2>
            <input type="text" id="youtube-url" placeholder="Enter YouTube URL">
            <button id="analyze-button">Analyze</button>
            <div id="analysis-result"></div>
        </div>
        <div class="parag">
            <h1>An Innovative Approach to Youtube Video Downlad
            </h1>
            <p>In today's fast-paced digital world, the need for quick, reliable, and efficient video downloading has never been greater. Whether you're saving a tutorial for offline viewing, archiving content for future reference, or simply building a personal media library, Videum Vault AI is here to make the process seamless.<br/><br/><br/>

Videum Vault AI represents the next generation of YouTube video downloading. We've reimagined the traditional downloader, infusing it with cutting-edge technology and a user-centric design, ensuring that every download is not only fast but also incredibly easy.
<h3 style="color:#f7f7f8;">Why Choose Videum Vault AI?</h3>
<ul>
<li>
Speed and Efficiency: Our platform is optimized to provide the fastest download speeds possible, ensuring that your videos are ready in no time.</li><br/><br/>

<li>User-Friendly Interface: With a clean, simple layout and intuitive controls, Videum Vault AI offers a stress-free experience for users of all technical levels.</li><br/><br/>

<li>Dynamic Backgrounds: Experience a visually appealing interface that features animated, colored backgrounds, adding a touch of style to your downloading process.

<li>Seamless Integration: No need to worry about complicated redirects or additional pages. Everything you need is on a single, streamlined page.</li><br/><br/>

<li>Smart Download Notifications: Our system will keep you informed about your download status in real time, eliminating the guesswork.</li><br/><br/><br/></ul>

<h3 style="color:#f7f7f8;">How It Works</h3>
<ol>
<li>Enter the URL: Simply paste the YouTube video URL into the provided field.</li><br/><br/>

<li>Download: Click the download button. If the video is ready for download, you'll get a direct link. If not, we'll handle the rest, and you'll be notified as soon as it's ready.</li><br/><br/>

<li>Enjoy: Download your video and enjoy it on any device, anytime, anywhere.</li><br/><br/></ol>

<h3 style="color:#f7f7f8;">Join the Revolution</h3><br/>
Experience the future of video downloading today with Videum Vault AI. Our innovative approach ensures that your favorite content is always just a click away.<br/>

Thank you for choosing Videum Vault AI – where simplicity meets innovation.
</p>
        </div>
        <footer>
            &copy; 2024 By Muunsparks to Society
        </footer>
<script>
    document.getElementById('analyze-button').addEventListener('click', function() {
    const youtubeUrl = document.getElementById('youtube-url').value;
    
    if (youtubeUrl) {
        fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: youtubeUrl })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('analysis-result').innerText = data.analysis;
        })
        .catch(error => {
            document.getElementById('analysis-result').innerText = 'Error analyzing video.';
        });
    } else {
        document.getElementById('analysis-result').innerText = 'Please enter a valid YouTube URL.';
    }
});
</script>
    </body>
    </html>"""

@app.route('/analyze', methods=['POST'])
def analyze_video():
    data = request.get_json()
    youtube_url = data.get('url')
    title, description = get_video_details(youtube_url[-11:])
    if youtube_url:
        prompt = f"{youtube_url} Title:{title} Description:{description}    What is this video about? And video suggestions"
        response = model.generate_content(prompt)
        
        return jsonify({'analysis': response.text})
    else:
        return jsonify({'analysis': 'Invalid URL'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

