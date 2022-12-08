// Модель для хранения вопросов. Сохраняет и выдает по требованию экземпляры Question
class QuestionModel {
	questions = []

	addQuestion(question) {
		this.questions.push(question)
	}

	getQuestion(ind) {
		return this.questions[ind]
	}

	getSeqAnswers() {
		return this.questions.map(e => e.result)
	}
}

// Контроллер процесса тестирования.
class TestController {
	state = -1
	model = new QuestionModel()
	fetcher = new Fetcher()
	processNode = document.querySelector('#process')
	testResult = new TestResult()
	spinner = new Spinner()

	constructor(testID) {
		this.showWaiting()
		this.fetcher.fetch(`http://localhost:8000/test/${testID}/data/`).then(response => {
			return response.json()
		}).then(json => {
			return json.forEach(e => this.model.addQuestion(new Question(e, this)))
		}).then( () => {
			this.hideWaiting()
			this.nextQuestion()
		})
	}

	nextQuestion() {
		if (this.state !== -1) this.model.getQuestion(this.state).hide()
		this.state += 1
		let nextQuestion = this.model.getQuestion(this.state)
		if (!nextQuestion) {
			let seq = this.model.getSeqAnswers()
			this.testResult.sendResult(
				seq.filter(e => e === true).length,
				seq.filter(e => e === false).length
			)
			return
		}
		nextQuestion.show()
	}

	showWaiting() {
		this.spinner.show()
	}

	hideWaiting() {
		this.spinner.hide()
	}

	async answerProcess(e) {
		e.preventDefault()
		this.showWaiting()
		this.model.getQuestion(this.state).setResult(await this.checkAnswer(e.target))
		this.nextQuestion()
		this.hideWaiting()
	}

	async checkAnswer(form) {
		let csrf = Cookie.getCookie('csrftoken');
		let fd = new FormData(form)
		let options = {
			method: 'POST',
			headers: {'X-CSRFToken': csrf},
			mode: 'same-origin',
			body: fd,
		}
		let response = await this.fetcher.fetch(`http://localhost:8000/question/${form.id}/check/`, options)
		let json = await response.json()
		return json.result
	}

	exit(e) {
		if (this.model.getQuestion(this.state)) {
			e.preventDefault()
			return e.returnValue = 'При выходе из системы попытка будет использована'
		}
	}
}


// Извлечение данных с сервера
class Fetcher {
	async fetch(url, options) {
		const response = await fetch(url, options)
		if (!response.ok) throw 'Загрузка не удалась'
		return response
	}
}


// Модель вопроса. Хранит в себе node вопроса и результат ответа на вопрос.
class Question {
	node
	result
	controller

	constructor(data, controller) {
		this.node = this.createNode(data)
		this.controller = controller
	}

	createNode(data) {
		let node = document.createElement('div')
		node.classList.add('question')
		let text = document.createElement('div')
		text.classList.add('question-text')
		text.innerText = data.title
		node.appendChild(text)
		let form = document.createElement('form')
		form.id = data.id
		node.appendChild(form)

		data.answers.forEach(e => {
			let label = document.createElement('label')
			let input = document.createElement('input')
			label.innerText = e.title
			input.type = data.type_answer
			input.name = 'result'
			input.value = e.pk
			label.appendChild(input)
			form.appendChild(label)
		})

		let button = document.createElement('button')
		button.type = 'submit'
		button.innerText = 'Принять ответ'
		form.addEventListener('submit', (e) => this.controller.answerProcess(e))
		form.appendChild(button)
		node.appendChild(form)
		return node
	}

	setResult(result) {
		this.result = result
	}

	show() {
		this.controller.processNode.appendChild(this.node)
	}

	hide() {
		this.controller.processNode.removeChild(this.node)
	}
}


// Модель формы для сохранения результатов тестирования.
class TestResult {
	node

	constructor() {
		this.node = document.querySelector('#result')
	}

	sendResult(correct_answer, wrong_answer) {
		this.node.querySelector(`#id_correct_answers`).value = correct_answer
		this.node.querySelector(`#id_wrong_answers`).value = wrong_answer
		this.node.querySelector(`#id_is_completed`).checked = true
		this.node.submit()
	}
}


// Модель спиннера, отвечающего за отображение контента во время загрузки и обработки данных
class Spinner {
	node

	constructor() {
		this.node = document.querySelector('#spinner')
	}

	show() {
		this.node.classList.remove('disabled')
	}

	hide() {
		this.node.classList.add('disabled')
	}
}


// Обработчик cookie. Требуется для извлечения csrf токена для отправки ajax формы post запросом
class Cookie {
	static getCookie(name) {
		let cookieValue = null;
		if (document.cookie && document.cookie !== '') {
			const cookies = document.cookie.split(';');
			for (let i = 0; i < cookies.length; i++) {
				const cookie = cookies[i].trim();
				if (cookie.substring(0, name.length + 1) === (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}
}


// Инициализатор тестирования
class TestProcess {
	static testController

	static start(testID) {
		this.testController = new TestController(testID)
		window.addEventListener('beforeunload', (e) => this.testController.exit(e))
	}
}
