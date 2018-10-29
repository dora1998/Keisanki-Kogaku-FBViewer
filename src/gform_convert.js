filebody = ""

textbox = document.querySelectorAll(".quantumWizTextinputPaperinputInput")
textbox.forEach(function(item) {
	keyword = item.attributes["aria-label"].value
	if (keyword.startsWith("ID番号")) {
		keyword = "ceid"
	} else if (keyword.startsWith("パスワード")) {
		keyword = "passwd"
	}
	filebody += keyword + ": " + item.value + "\n"
})

kanso_box= document.querySelector(".quantumWizTextinputPapertextareaInput")
filebody += "kanso: " + kanso_box.value + "\n"

title = document.querySelector(".freebirdFormviewerViewHeaderTitle").textContent

completion({
	title: title,
	body: filebody
})