import axios from '../plugins/axios.js'

export const search = {
  fetchEnglish(keyword) {
    return axios.get(`/lines/search/english/${keyword}`)
  },
  fetchKorean(keyword) {
    return axios.get(`lines/search/korean/${keyword}`)
  }
}
