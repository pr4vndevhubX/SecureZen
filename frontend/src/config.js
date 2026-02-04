/**
 * Global Configuration for the AI SOC Dashboard
 */

// Use your computer's local network IP address so others can access the API
const MACHINE_IP = '192.168.217.126';

export const API_BASE_URL = `http://${MACHINE_IP}:5000`;

// RAG Service is usually on port 8001
export const RAG_SERVICE_URL = `http://${MACHINE_IP}:8001`;

export default {
    API_BASE_URL,
    RAG_SERVICE_URL
};
