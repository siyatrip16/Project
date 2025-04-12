import streamlit as st
from datetime import datetime
import uuid

from ciphera_model import img_filter, vid_filter, aud_filter, txt_filter

# Initialize session_state for posts, comments, and messages if not already set
if "posts" not in st.session_state:
    st.session_state.posts = []  # Each post: {"id", "user", "content", "image", "timestamp", "comments": []}
if "messages" not in st.session_state:
    st.session_state.messages = []  # Each message: {"id", "sender", "receiver", "message", "timestamp"}

# Function to add a new post
def add_post(user, content, image):
    new_post = {
        "id": str(uuid.uuid4()),
        "user": user,
        "content": content,
        "image": image,
        "timestamp": datetime.now(),
        "comments": []
    }
    st.session_state.posts.insert(0, new_post)

# Function to add a new comment to a post
def add_comment(post_id, commenter, comment):
    for post in st.session_state.posts:
        if post["id"] == post_id:
            post["comments"].append({
                "id": str(uuid.uuid4()),
                "user": commenter,
                "comment": comment,
                "timestamp": datetime.now()
            })

# Function to add a new message
def send_message(sender, receiver, message):
    new_message = {
        "id": str(uuid.uuid4()),
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "timestamp": datetime.now()
    }
    st.session_state.messages.append(new_message)

# Sidebar for navigation and user info
st.sidebar.title("Dashboard")
user = st.sidebar.text_input("Enter your username:", value="guest")
# Top Horizontal Dashboard
st.markdown("---")
col1, col2, col3, col4= st.columns(4)
with col1:
    if st.button("Home"):
        st.session_state.menu = "Home"
with col2:
    if st.button("Upload"):
        st.session_state.menu = "Upload Post"
with col3:
    if st.button("Messages"):
        st.session_state.menu = "Messages"
with col4:
    st.write("")  # Empty space or future "Settings"
st.markdown("---")
if "menu" not in st.session_state:
    st.session_state.menu = "Home"  # Default view

if st.session_state.menu == "Home":
    st.title("Home Feed")
    st.write("Scroll through posts below:")

    # Loop through posts and display them
    for post in st.session_state.posts:
        st.markdown(f"**{post['user']}**  _({post['timestamp'].strftime('%Y-%m-%d %H:%M:%S')})_")
        st.write(post["content"])
        if post["image"] is not None:
            if post["image"].type.startswith("video"):
                st.video(post["image"])
            else:
                st.image(post["image"], use_column_width=True)
        # Display comments
        if post["comments"]:
            st.markdown("**Comments:**")
            for comment in post["comments"]:
                st.markdown(f"* **{comment['user']}**: {comment['comment']}  _({comment['timestamp'].strftime('%H:%M')})_")
        # Comment form for this post
        with st.form(key=f"comment_{post['id']}"):
            cmt = st.text_input("Add a comment", key=f"cmt_{post['id']}")
            submit_comment = st.form_submit_button("Comment")
            if submit_comment and cmt:
                add_comment(post_id=post["id"], commenter=user, comment=cmt)
                st.rerun()  # Refresh the page to show the new comment
        st.markdown("---")

elif st.session_state.menu == "Upload Post":
    st.title("Create a New Post")
    with st.form(key="upload_post"):
        content = st.text_area("What's on your mind?")
        media_file = st.file_uploader("Upload an image or video", type=["png", "jpg", "jpeg", "mp4"])
        submit_post = st.form_submit_button("Post")
        if submit_post:
            # For demo purposes, image is stored in memory (bytes)
            add_post(user=user, content=content, image=media_file)
            st.success("Post uploaded!")
            st.rerun()

elif st.session_state.menu == "Messages":
    st.title("Direct Messaging")
    st.write("Send and view your messages.")
    
    # Form to send a new message
    with st.form(key="new_message"):
        receiver = st.text_input("Receiver username")
        message_text = st.text_area("Message")
        send_btn = st.form_submit_button("Send Message")
        if send_btn and receiver and message_text:
            send_message(sender=user, receiver=receiver, message=message_text)
            st.success("Message sent!")
            st.rerun()

    # Display messages for the current user (as sender or receiver)
    user_messages = [m for m in st.session_state.messages if m["sender"] == user or m["receiver"] == user]
    if user_messages:
        st.subheader("Your Messages")
        for msg in user_messages:
            sender_info = f"From: {msg['sender']}" if msg['sender'] != user else "From: You"
            receiver_info = f"To: {msg['receiver']}" if msg['receiver'] != user else "To: You"
            st.markdown(f"**{sender_info} | {receiver_info}**  _({msg['timestamp'].strftime('%Y-%m-%d %H:%M')})_")
            st.write(msg["message"])
            st.markdown("---")
    else:
        st.write("No messages yet.")
for post in st.session_state.posts:
    clean_text = txt_filter(post["content"])
    st. markdown(f"**{post['user']}**")
    
    if post["image"] and not img_filter(post["image"].name):
        st.image(post["image"])
    else:
        st.warning("Sensitive image Removed")
    
    st.write(clean_text)
    
if not vid_filter(video_path) and not aud_filter(video_path):
    st.video(video_file)
else:
    st.warning("The Video contains NSFW or offensive audio and had been removed")
# A simple footer
st.sidebar.markdown("© 2025 Demo Social Media Platform")