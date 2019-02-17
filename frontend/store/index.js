import Vuex from 'vuex';
import linesModule from './modules/lines';

const store = () => new Vuex.Store({
  modules: {
    lines: linesModule,
  }
})

export default store;
