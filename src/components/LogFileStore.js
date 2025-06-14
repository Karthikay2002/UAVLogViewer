import { reactive } from 'vue'

function getOrCreateSessionId () {
    let sid = localStorage.getItem('session_id')
    if (!sid) {
        sid = 'sess-' + Math.random().toString(36).slice(2) + Date.now()
        localStorage.setItem('session_id', sid)
    }
    return sid
}

export const logFileStore = reactive({
    filename: '',
    sessionId: getOrCreateSessionId()
})
