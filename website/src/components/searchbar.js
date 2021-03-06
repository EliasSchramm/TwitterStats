import React from 'react';
import ReactDOM from 'react-dom';
import { Redirect } from 'react-router';

class TagOrHashtag_Error_Banner extends React.Component {
    constructor(probs){
        super(probs)
    }

    render(){
        return(
            <div class="alert alert-danger" role="alert">
                Search needs to start with "#" or "@"
            </div>
        );
    }
}

class Searchbar extends React.Component {
    constructor(probs){
      super(probs);     

      this.state = {
          search_key:"",
          show_t_ht_err:false,
          redirect:""
      }
      
      this.handleSubmit = this.handleSubmit.bind(this);
      this.handleChange = this.handleChange.bind(this);
    }   

    handleSubmit(e){
        e.preventDefault();    

        let val = this.state.search_key;
        console.log(val);
        if(!val.startsWith("#") && !val.startsWith("@")){
            this.setState({
                show_t_ht_err:true
            })
            return;
        }else if(val.length < 2) return;

        let prefix = val.startsWith("#") ? "hashtag" : "tag";
        
        this.setState({
            redirect:encodeURI("/history/" + prefix + "/" + val.substr(1))
        })
        this.forceUpdate()
        return;
    }

    handleChange(e){
        let ele = e.target;
        this.setState({
            search_key:ele.value
        })
    }   

    render(){   
        let err = this.state.show_t_ht_err ? <TagOrHashtag_Error_Banner /> : "";
        let redirect = this.state.redirect != "" ? <Redirect to={this.state.redirect} /> : "";

        return (
            <div class="form">
                {redirect}
                <form class="p-3" onSubmit={this.handleSubmit}>
                    <div class="input-group">
                        <input type="text" name="search" id="search" class="form-control form-control-lg rounded-0 eps" placeholder="Search for an tag or hashtag..." autocomplete="off" value={this.state.search_key} onInput={this.handleChange} required />
                        <div class="input-group-append">
                            <input type="button" name="submit" value="Search" class="btn btn-lg rounded-0 eps" onClick={this.handleSubmit} />
                        </div>
                    </div>
                </form>

                {err}
            </div>
        );      
    }  
  }

  export default () => {
    return (
        <Searchbar />
    )
}