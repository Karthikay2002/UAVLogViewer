<template>
    <div class="chat-panel">
        <!-- Header -->
        <div class="chat-header">
            <div class="header-left">
                <router-link to="/" class="back-button">
                    <i class="fas fa-arrow-left"></i>
                    Back to Home
                </router-link>
                <h2>UAV Assistant</h2>
            </div>
            <button
                v-if="onAnalyzeLogs"
                @click="onAnalyzeLogs"
                :disabled="isAnalyzing"
                class="analyze-button"
            >
                <span v-if="isAnalyzing" class="loading-spinner"></span>
                {{ isAnalyzing ? 'Analyzing...' : 'Analyze Logs' }}
            </button>
        </div>

        <!-- File Upload -->
        <div class="upload-container">
            <input type="file" @change="handleFileUpload" accept=".bin,.log,.tlog,.ulg" />
            <span v-if="logFileStore.filename" class="filename-label">File: {{ logFileStore.filename }}</span>
            <div v-if="logFileStore.filename" class="uploaded-label">
                ✅ Uploaded for Assistant & Viewer: {{ logFileStore.filename }}
            </div>
        </div>

        <!-- Messages -->
        <div class="messages-container" ref="messagesContainer">
            <transition-group name="message">
                <div
                    v-for="message in messages"
                    :key="message.id"
                    :class="['message', message.role]"
                >
                    <div class="message-content">
                        <div v-html="formatMessage(message.content)"></div>
                        
                        <!-- Display visualizations if present -->
                        <div v-if="message.visualizations && message.visualizations.length > 0" class="visualizations-container">
                            <h4>📊 Generated Visualizations</h4>
                            <div class="plots-grid">
                                <div v-for="plot in message.visualizations" :key="plot.filename" class="plot-item">
                                    <h5>{{ plot.title }}</h5>
                                    <img :src="plot.url" :alt="plot.title" class="plot-image" @click="openImageModal(plot)" />
                                    <p class="plot-description">{{ plot.description }}</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Display reports if present -->
                        <div v-if="message.reports && message.reports.length > 0" class="reports-container">
                            <h4>📋 Generated Reports</h4>
                            <div class="reports-list">
                                <div v-for="report in message.reports" :key="report.filename" class="report-item">
                                    <a :href="report.url" target="_blank" class="report-link">
                                        📄 {{ report.title || report.filename }}
                                    </a>
                                    <p class="report-description">{{ report.description }}</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="message-timestamp">{{ formatTime(message.timestamp) }}</div>
                    </div>
                </div>
            </transition-group>
        </div>

        <!-- Input -->
        <form @submit.prevent="handleSubmit" class="input-container">
            <input
                v-model="input"
                type="text"
                placeholder="Ask about your UAV logs... Try: 'I need visual reports for this plz' or 'Generate visualizations'"
                :disabled="isLoading || !logFileStore.filename"
            />
            <button type="submit" :disabled="isLoading || !input.trim() || !logFileStore.filename">
                <span v-if="isLoading" class="loading-spinner"></span>
                <span v-else>Send</span>
            </button>
        </form>
        
        <!-- Image Modal -->
        <div v-if="selectedImage" class="image-modal" @click="closeImageModal">
            <div class="modal-content" @click.stop>
                <button class="modal-close" @click="closeImageModal">&times;</button>
                <img :src="selectedImage && selectedImage.url" :alt="selectedImage && selectedImage.title" class="modal-image" />
                <h3>{{ selectedImage && selectedImage.title }}</h3>
                <p>{{ selectedImage && selectedImage.description }}</p>
            </div>
        </div>
    </div>
</template>

<script>
/* eslint-disable */
/* eslint-disable-next-line */
/* eslint-disable template-curly-spacing */
/* eslint-disable no-unused-vars */
import { ref, nextTick, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { logFileStore } from './LogFileStore'

export default {
    name: 'ChatPanel',
    props: {
        onAnalyzeLogs: {
            type: Function,
            default: null
        },
        isAnalyzing: {
            type: Boolean,
            default: false
        }
    },
    setup () {
        const messages = ref([])
        const input = ref('')
        const isLoading = ref(false)
        const messagesContainer = ref(null)
        const selectedImage = ref(null)

        const scrollToBottom = async () => {
            await nextTick()
            if (messagesContainer.value) {
                messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
            }
        }

        watch(messages, scrollToBottom, { deep: true })

        const formatMessage = (content) => {
            if (!content) return ''
            return DOMPurify.sanitize(marked(content))
        }

        const formatTime = (timestamp) => {
            if (!timestamp) return ''
            return new Date(timestamp).toLocaleTimeString()
        }

        const openImageModal = (plot) => {
            if (plot) {
                selectedImage.value = plot
            }
        }

        const closeImageModal = () => {
            selectedImage.value = null
        }

        const handleFileUpload = async (event) => {
            const file = event?.target?.files?.[0]
            if (!file) return
            
            const formData = new FormData()
            formData.append('file', file)
            
            try {
                const response = await fetch('http://localhost:8000/upload', {
                    method: 'POST',
                    body: formData
                })
                
                if (!response.ok) {
                    const errorText = await response.text()
                    console.error('Upload failed:', response.status, errorText)
                    alert(`File upload failed! (Status: ${response.status}) ${errorText}`)
                    logFileStore.filename = ''
                    return
                }
                
                const data = await response.json()
                logFileStore.filename = data?.filename || ''
            } catch (error) {
                alert('File upload failed! (Network or CORS error)')
                console.error('File upload error:', error)
                logFileStore.filename = ''
            }
        }

        const fetchVisualizationsAndReports = async (requestStartTime) => {
            try {
                const [plotsResponse, reportsResponse] = await Promise.all([
                    fetch('http://localhost:8000/api/plots'),
                    fetch('http://localhost:8000/api/reports')
                ])
                
                const plotsData = await plotsResponse.json()
                const reportsData = await reportsResponse.json()
                
                // Filter to only include files created after the request started (within last 60 seconds)
                const cutoffTime = requestStartTime - 60
                
                return {
                    visualizations: plotsData.plots?.filter(plot => 
                        plot.created && plot.created > cutoffTime
                    ).map(plot => ({
                        filename: plot.filename,
                        url: plot.url.startsWith('http') ? plot.url : 'http://localhost:8000' + plot.url,
                        title: getPlotTitle(plot.filename),
                        description: getPlotDescription(plot.filename)
                    })) || [],
                    reports: reportsData.reports?.filter(report => 
                        report.created && report.created > cutoffTime
                    ).map(report => ({
                        filename: report.filename,
                        url: report.url.startsWith('http') ? report.url : 'http://localhost:8000' + report.url,
                        title: getReportTitle(report.filename),
                        description: getReportDescription(report.filename)
                    })) || []
                }
            } catch (error) {
                console.error('Error fetching visualizations:', error)
                return { visualizations: [], reports: [] }
            }
        }

        const getPlotTitle = (filename) => {
            if (filename.includes('comprehensive_dashboard')) {
                return '🚁 Comprehensive Flight Dashboard'
            } else if (filename.includes('detailed_battery_analysis')) {
                return '🔋 Detailed Battery Analysis'
            } else if (filename.includes('gps_navigation_analysis')) {
                return '🛰️ GPS & Navigation Analysis'
            } else if (filename.includes('altitude_analysis')) {
                return '📈 Altitude Analysis'
            } else if (filename.includes('battery_analysis')) {
                return '🔋 Battery Analysis'
            } else if (filename.includes('gps_analysis')) {
                return '🛰️ GPS Analysis'
            } else {
                return '📊 Flight Analysis Chart'
            }
        }

        const getPlotDescription = (filename) => {
            if (filename.includes('comprehensive_dashboard')) {
                return 'Complete flight overview with altitude profile, battery status, GPS performance, flight modes, and system health summary'
            } else if (filename.includes('detailed_battery_analysis')) {
                return 'In-depth battery analysis including voltage trends, distribution, health indicators, and performance metrics'
            } else if (filename.includes('gps_navigation_analysis')) {
                return 'GPS performance metrics including satellite count, accuracy (HDOP), quality distribution, and speed analysis'
            } else if (filename.includes('altitude_analysis')) {
                return 'Altitude profile analysis with statistics and distribution patterns'
            } else if (filename.includes('battery_analysis')) {
                return 'Battery voltage monitoring and health assessment'
            } else if (filename.includes('gps_analysis')) {
                return 'GPS satellite tracking and positioning accuracy analysis'
            } else {
                return 'Professional flight data visualization and analysis'
            }
        }

        const getReportTitle = (filename) => {
            if (filename.includes('flight_report')) {
                return '📋 Comprehensive Flight Report'
            } else if (filename.includes('safety_assessment')) {
                return '🛡️ Safety Assessment Report'
            } else if (filename.includes('telemetry_health')) {
                return '📡 Telemetry Health Report'
            } else {
                return '📄 Flight Analysis Report'
            }
        }

        const getReportDescription = (filename) => {
            if (filename.includes('flight_report')) {
                return 'Complete flight analysis report with safety assessment, telemetry health, and comprehensive analysis'
            } else if (filename.includes('safety_assessment')) {
                return 'Detailed safety evaluation and risk assessment of the flight'
            } else if (filename.includes('telemetry_health')) {
                return 'Telemetry data quality and completeness analysis'
            } else {
                return 'Detailed flight analysis and performance report'
            }
        }

        const handleSubmit = async () => {
            // Defensive checks for refs
            if (!input || !messages || !isLoading) {
                console.error('Refs not properly initialized')
                return
            }
            
            if (!input.value || !input.value.trim() || !logFileStore.filename) return

            const userInput = input.value || ''
            const userMessage = {
                id: Date.now() + Math.random(),
                role: 'user',
                content: userInput,
                timestamp: new Date()
            }

            messages.value?.push(userMessage)
            input.value = ''
            isLoading.value = true

            try {
                const requestStartTime = Date.now() / 1000 // Unix timestamp
                
                const payload = {
                    question: userInput,
                    filename: logFileStore.filename,
                    sessionId: logFileStore.sessionId || null
                }
                const response = await fetch('http://localhost:8000/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })

                if (!response.ok) {
                    const txt = await response.text()
                    throw new Error(txt)
                }

                const data = await response.json()

                // Check if visualizations were requested and fetch them
                const vizKeywords = ['visual', 'plot', 'chart', 'graph', 'dashboard', 'report', 'trend', 'image', 'picture', 'show', 'display']
                const requestedViz = vizKeywords.some(keyword => userInput.toLowerCase().includes(keyword))
                
                console.log('User input:', userInput)
                console.log('Requested visualizations:', requestedViz)
                
                let visualizations = []
                let reports = []
                
                if (requestedViz) {
                    // Only fetch plots/reports created after this request started
                    const vizData = await fetchVisualizationsAndReports(requestStartTime)
                    
                    visualizations = vizData?.visualizations || []
                    reports = vizData?.reports || []
                }
                
                console.log('Fetched recent visualizations:', visualizations.length)
                console.log('Fetched recent reports:', reports.length)

                const assistantMessage = {
                    id: Date.now() + Math.random(),
                    role: 'assistant',
                    content: data?.response || 'No response from backend.',
                    timestamp: new Date(),
                    visualizations,
                    reports
                }

                messages.value?.push(assistantMessage)
            } catch (error) {
                const errorMessage = {
                    id: Date.now() + Math.random(),
                    role: 'assistant',
                    content: `❌ Error: ${error?.message || 'Unknown error occurred'}`,
                    timestamp: new Date()
                }
                messages.value?.push(errorMessage)
                console.error('Error sending message:', error)
            } finally {
                isLoading.value = false
            }
        }

        return {
            messages,
            input,
            isLoading,
            logFileStore,
            messagesContainer,
            selectedImage,
            handleSubmit,
            handleFileUpload,
            formatMessage,
            formatTime,
            openImageModal,
            closeImageModal
        }
    }
}
</script>

<style scoped>
.chat-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: #f9fafb;
    overflow: hidden;
}

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background-color: #2563eb;
    color: white;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.back-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.2s;
}

.back-button:hover {
    opacity: 0.8;
}

.chat-header h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
}

.analyze-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: white;
    color: #2563eb;
    border: none;
    border-radius: 0.375rem;
    font-weight: 500;
    transition: background-color 0.2s;
    cursor: pointer;
}

.analyze-button:hover:not(:disabled) {
    background-color: #f0f9ff;
}

.analyze-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.message {
    display: flex;
    max-width: 80%;
}

.message.user {
    margin-left: auto;
}

.message-content {
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.message.user .message-content {
    background-color: #2563eb;
    color: white;
}

.message.assistant .message-content {
    background-color: white;
    color: #1f2937;
}

.message-timestamp {
    font-size: 0.75rem;
    opacity: 0.7;
    margin-top: 0.5rem;
}

.input-container {
    display: flex;
    gap: 0.5rem;
    padding: 1rem;
    background-color: white;
    border-top: 1px solid #e5e7eb;
}

.input-container input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    outline: none;
    transition: border-color 0.2s;
}

.input-container input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

.input-container button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-weight: 500;
    transition: background-color 0.2s;
    cursor: pointer;
}

.input-container button:hover:not(:disabled) {
    background-color: #1d4ed8;
}

.input-container button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.loading-spinner {
    width: 1rem;
    height: 1rem;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* Message transition animations */
.message-enter-active,
.message-leave-active {
    transition: all 0.3s ease;
}

.message-enter-from {
    opacity: 0;
    transform: translateY(20px);
}

.message-leave-to {
    opacity: 0;
    transform: translateY(-20px);
}

.upload-container {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f3f4f6;
    border-bottom: 1px solid #e5e7eb;
}

.filename-label {
    font-size: 0.95rem;
    color: #2563eb;
    font-weight: 500;
}

.uploaded-label {
    font-size: 0.75rem;
    color: #2563eb;
    font-weight: 500;
}

.visualizations-container {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #f8fafc;
    border-radius: 0.5rem;
    border: 1px solid #e2e8f0;
}

.visualizations-container h4 {
    margin: 0 0 1rem 0;
    color: #1e293b;
    font-size: 1.1rem;
}

.plots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
}

.plot-item {
    background: white;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.plot-item h5 {
    margin: 0 0 0.5rem 0;
    color: #1e293b;
    font-size: 1rem;
}

.plot-image {
    max-width: 100%;
    height: auto;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: transform 0.2s;
    margin-bottom: 0.5rem;
}

.plot-image:hover {
    transform: scale(1.02);
}

.plot-description {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0;
}

.reports-container {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #f8fafc;
    border-radius: 0.5rem;
    border: 1px solid #e2e8f0;
}

.reports-container h4 {
    margin: 0 0 1rem 0;
    color: #1e293b;
    font-size: 1.1rem;
}

.reports-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.report-item {
    background: white;
    padding: 0.75rem;
    border-radius: 0.375rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.report-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    color: #2563eb;
    font-weight: 500;
    transition: color 0.2s;
}

.report-link:hover {
    color: #1d4ed8;
}

.report-description {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0.25rem 0 0 0;
}

.image-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    padding: 2rem;
}

.modal-content {
    position: relative;
    background-color: white;
    padding: 2rem;
    border-radius: 0.5rem;
    max-width: 90vw;
    max-height: 90vh;
    overflow: auto;
    text-align: center;
}

.modal-close {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: none;
    border: none;
    font-size: 2rem;
    color: #6b7280;
    cursor: pointer;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.2s;
}

.modal-close:hover {
    background-color: #f3f4f6;
}

.modal-image {
    max-width: 100%;
    max-height: 70vh;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}

.modal-content h3 {
    margin: 0 0 0.5rem 0;
    color: #1e293b;
}

.modal-content p {
    margin: 0;
    color: #64748b;
}
</style>
