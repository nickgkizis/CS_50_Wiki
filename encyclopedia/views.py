from django.shortcuts import render
from markdown2 import Markdown
from . import util
from django import forms
import secrets
from django.http import HttpResponseRedirect
from django.urls import reverse


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    content = forms.CharField(widget=forms.Textarea, label="Content")

def mdToHtml(title):
    text = util.get_entry(title)
    if text == None:
        return None
    else:
        return Markdown().convert(text)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request,title):
    content = mdToHtml(title)
    if content == None:
        return render(request,"encyclopedia/error.html",{
            "message": "404 Not found"
        })
    else:
        return render(request,"encyclopedia/entry.html",{
            "title": title,
            "content": content
        })

def newEntry(request):
    if request.method == "GET":
        form = NewEntryForm()
        return render(request, "encyclopedia/newEntry.html", {"form": form})
    else:
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title) is not None:
                return render(request, "encyclopedia/error.html", {
                    "message": "An entry with this title already exists."
                })
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', args=[title]))
        else:
            return render(request, "encyclopedia/newEntry.html", {"form": form})




def edit(request):
    if request.method == "POST":
        title = request.POST['entry_title']
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })

def save_edit(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        util.save_entry(title, content)
        html_content = mdToHtml(title)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content
        })


def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    html_content = mdToHtml(randomEntry)
    return render(request,"encyclopedia/entry.html",{
        "title": randomEntry,
        "content": html_content
    })

def search(request):
    if request.method == "POST":
        entry_search = request.POST['q']
        html_content = mdToHtml(entry_search)
        
        if html_content is not None:
            return render(request, "encyclopedia/entry.html", {
                "title": entry_search,
                "content": html_content
            })
        else:
            subStringEntries = []
            for entry in util.list_entries():
                if entry_search.lower() in entry.lower():
                    subStringEntries.append(entry)
            
            if subStringEntries:
                return render(request, "encyclopedia/search.html", {
                    "subStringEntries": subStringEntries
                })
            else:
                return render(request, "encyclopedia/error.html", {
                    "message": "No matching entries found."
                })

        



