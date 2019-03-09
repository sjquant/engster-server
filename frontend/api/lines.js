import axios from '../plugins/axios.js'

const searchLineEnglish = (keyword) => {
  return axios.get(`/lines/search/english/${keyword}`)
}

export {
  searchLineEnglish
}
