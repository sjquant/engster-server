import axios from 'axios'

export default axios.create({
  baseURL: process.env.baseUrl,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
})
