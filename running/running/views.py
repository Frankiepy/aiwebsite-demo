from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import ContactForm
import bleach
from bleach import clean
from urllib.parse import quote  # Add this import

import os
import openai
from bs4 import BeautifulSoup
#openai.organization = "org-TE9SDFD62sNgNGrLZ8S0ESaZ"

def create_static_site(user_input):
    openai.api_key = "API KEY"
    openai.Model.list()

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a website generator. You listen to the user's website ideas and write html code to create a website for them. Also be very descriptive in img alt tags about what the image is suppose to be. Also only return the html, nothing else."},
        {"role": "user", "content": user_input}
    ]
    )

    html_text = completion.choices[0].message['content']

    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html_text, 'html.parser')

    # Find all <img> tags
    img_tags = soup.find_all('img')

    # Extract the 'src' attribute from each <img> tag
    img_sources = []
    try:
        img_sources = [img['alt'] for img in img_tags]
    except Exception:
        try:
            img_sources = [img['src'] for img in img_tags]
        except Exception:
            pass

    image_links = []
    for img in img_sources:
        response = openai.Image.create(prompt=img_sources[0],n=1,size="1024x1024")
        image_url = response['data'][0]['url']
        image_links.append(image_url)


    img_tags = soup.find_all('img')

    html_add_on = ''

    # Loop through each <img> tag and change the 'src' attribute
    i = 0
    for img in img_tags:
        # Get the current 'src' attribute value
        current_src = img['src']
    
        # Modify the 'src' attribute to change the image source name
        # You can manipulate the 'current_src' to create a new name
        # For example, let's add "_new" to the existing name
        new_src = image_links[i]
    
        # Update the 'src' attribute with the new source name
        img['src'] = new_src
        i += 1

    # Print the modified HTML content
    final_html = soup.prettify() + html_add_on

    print(final_html)
    return final_html



def front(request):
    return render(request, 'front_page.html')


def contact_view(request):
    safe_message = ''
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Retrieve and sanitize the message
            html_content = form.cleaned_data['html_content']

            html_content = create_static_site(str(html_content))
            
            html_content = quote(html_content)  # URL-encode the message
            # Do something with the valid form data

            # Redirect to the success page with the URL-encoded message
            #return redirect('success', html_content=html_content)
            decoded_message = unquote(html_content)
            safe_message = mark_safe(decoded_message)
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form, 'html_content': safe_message})


from django.utils.safestring import mark_safe
from urllib.parse import unquote  # Add this import

def success_view(request, html_content):
    decoded_message = unquote(html_content)
    safe_message = mark_safe(decoded_message)
    return render(request, 'success.html', {'html_content': safe_message})
