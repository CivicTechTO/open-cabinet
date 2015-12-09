var React = require('react');
var request = require('superagent');
var DatePicker = require('react-datepicker');
var ReactPaginate = require('react-paginate');



var SearchPage = React.createClass({


  getInitialState: function() {
    return {
                orders: [],
                result_count: false,
                limit: 50,
                total_count: false,
                offset: 0,
                page_num: 1,
                startDate: null,
                endDate: null,
                keywords: "",
                act: "",
                dept: "",
                pcnumber: "",
                bill: "",
                apiRootURL: "/api/orders"
                }
  },




  _convertDate: function( date ){
      var dateComps = date.format('L').toString().split("/");
      var newDate = dateComps[2] + '-' + dateComps[0] + '-' + dateComps[1];
      newDate = encodeURIComponent( newDate );
      return newDate;
  },

  handleChangeStart: function(date) {
    this.setState({ startDate: date });

  },

  handleChangeEnd: function(date) {
    this.setState({ endDate: date });
  },

  changePC: function(event) {
    this.setState({ pcnumber : event.target.value });
  },

  changeKeywords: function(event) {
    this.setState({ keywords: event.target.value });
  },

  changeAct: function(event) {
    this.setState({ act: event.target.value });
  },

  changeDept: function(event) {
    this.setState({ dept: event.target.value });
  },

  changeBill: function(event) {
    this.setState({ bill: event.target.value });
  },




    _loadCallbackFn: function( err, res ){
      if (res.status == 200) {
        var orders = res.body.results ;
        var current_count = res.body.pagination['current_count'] ;
        var total_count = res.body.pagination['total_count'] ;
        this.setState({ orders: orders, result_count: current_count, total_count: total_count });
        var pageNum = Math.ceil( this.state.total_count/this.state.limit ) ;
        this.setState({ pageNum: pageNum });
      }

    },

    loadOrders: function(){
      request
          .get( this.state.apiRootURL)
          .set('Accept', 'application/json')
          .end( this._loadCallbackFn );
    },

    searchOrders: function(event){
        var params = {};
        params['offset'] = this.state.offset;

        // Search button pressed
        if (event != undefined){
            event.preventDefault();
            params['offset'] = 0;
            this.setState({ offset: 0 });

        }
        // Fetch individual order
        if ( this.state.pcnumber != ""){
            request
                .get(this.state.apiRootURL+'/'+this.state.pcnumber )
                .set('Accept', 'application/json')
                .end( this._loadCallbackFn );
        }

        // Fetch a bunch of orders
        else{
            
            if (  (this.state.endDate != null) & (this.state.startDate != null)  ){
                params['startDate'] = this._convertDate(this.state.startDate);
                params['endDate'] = this._convertDate(this.state.endDate);
            }
            if ( this.state.act != "" ){
                params['actName'] = encodeURIComponent(this.state.act);
            }
            if ( this.state.dept != "" ){
                params['deptName'] = encodeURIComponent(this.state.dept);
            }
            if ( this.state.bill != "" ){
                params['billName'] = encodeURIComponent(this.state.bill);
            }
            if ( this.state.keywords != "" ){
                params['keywords'] = encodeURIComponent(this.state.keywords);
            }
                            
            request
                .get(this.state.apiRootURL)
                .query( params )
                .set('Accept', 'application/json')
                .end( this._loadCallbackFn );

        };

    },

   componentDidMount: function(){
        this.loadOrders();
   },


  handlePageClick: function(data) {
      var selected = data.selected;
      var offset = Math.ceil(selected * this.state.limit);

      this.setState({offset: offset}, function(){
        this.searchOrders();
      }.bind(this));

      this.searchOrders();


  },



  render: function() {

    var pcnumber = this.state.pcnumber, dept=this.state.dept, act=this.state.act, bill=this.state.bill, keywords=this.state.keywords;
    var startDate = this.state.startDate, endDate =  this.state.endDate;

    var spitTable = this.state.orders.map( function( order, index ){

        var att_urls = order.attachment_urls.map( function(url, index) {
            return <a target="_blank" href={url} key={index}>{index+1}</a>
        });

        var acts = order.acts.map( function(act, index){
            var act_url = "http://www.canlii.org/en/#search/type=legislation&id=".concat( encodeURIComponent( act ) );
            return <a target="_blank" href={act_url} key={index}>{act}</a>
        });

        return(
          <tbody key={index}>
              <tr>
                  <td><a target="_blank" href={order.url}><b>{order.id}</b></a></td>
                  <td>{order.pub_date}</td>
                  <td>{order.chapter}</td>
                  <td>{order.bill}</td>
                  <td>{order.departments.join(" ")}</td>
              </tr>
              <tr >
                  <th>Act</th>
                  <td colSpan="4">{acts}</td>
              </tr>              
              <tr >
                  <th>Precis</th>
                  <td colSpan="4"> {order.precis} </td>
              </tr>

              { (order.attachments.length != 0 ) &&
                <tr >
                    <th>Attachment</th>
                    <td colSpan="4"> { att_urls } </td>
                </tr>
              }


              { (order.reg_id != null) &&
                <tr >
                    <th>Registration</th>
                    <td colSpan="4"><b>Registration ID</b>: {order.reg_id} <b>Registration Date</b>: {order.reg_date} </td>
                </tr>                

              }


              <tr >
                  <th></th>
                  <td colSpan="4">  </td>
              </tr>
          </tbody>
          )
    });

    return (

          <div>


          <form className="form-horizontal" role="form">

            <div className="form-group">
                <label className="col-sm-2">PC Number (YYYY####)</label>
                <div className="col-sm-3">
                    <input  type="text" className="form-control" placeholder="PC Number" value={pcnumber} onChange={this.changePC} />
                </div>
            </div>
            
            <div className="form-group">
              <label className="col-sm-2">Start Date</label>
              <DatePicker selected={startDate} onChange={this.handleChangeStart} placeholderText= 'Select a date' />
            </div>

            <div className="form-group">
              <label className="col-sm-2">End Date</label>
              <DatePicker selected={endDate} onChange={this.handleChangeEnd} placeholderText= 'Select a date' />
            </div>


            <div className="form-group">
                <label className="col-sm-2">Keywords</label>
                <div className="col-sm-3">
                    <input  type="text" className="form-control" placeholder="Keywords" value={keywords} onChange={this.changeKeywords} />
                </div>
            </div>

            <div className="form-group">
                <label className="col-sm-2">Act</label>
                <div className="col-sm-3">
                    <input  type="text" className="form-control" placeholder="Act" value={act} onChange={this.changeAct} />
                </div>
            </div>

            <div className="form-group">
                <label className="col-sm-2">Department</label>
                <div className="col-sm-3">
                    <input  type="text" className="form-control" placeholder="Department" value={dept} onChange={this.changeDept} />
                </div>
            </div>

            <div className="form-group">
                <label className="col-sm-2">Bill</label>
                <div className="col-sm-3">
                    <input  type="text" className="form-control" placeholder="Bill" value={bill} onChange={this.changeBill} />
                </div>
            </div>
            

            <br />
            <div className="form-group col-sm-3">
            <button type="submit" className="btn btn-default" onClick={this.searchOrders} >Search</button>
            </div>

          </form>



          <br />



          <div className="row">

          { this.state.result_count && 
              <div> <b>Results: { Math.max(this.state.offset, 1) } - { Math.min( (this.state.result_count + this.state.offset),this.state.total_count)}  / {this.state.total_count}
              </b></div> 
          }

          </div>
          <br />


          <div className="row">




        <ReactPaginate previousLabel={"previous"}
                       nextLabel={"next"}
                       breakLabel={<li className="break"><a href="">...</a></li>}
                       pageNum={this.state.pageNum}
                       marginPagesDisplayed={2}
                       pageRangeDisplayed={7}
                       clickCallback={this.handlePageClick}
                       containerClassName={"pagination"}
                       subContainerClassName={"pages pagination"}
                       activeClassName={"active"} />

        </div>


        <br />


        <div className="row">
          <table className="table table-bordered">

              <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Date</th>
                    <th>Chapter</th>
                    <th>Bill</th>
                    <th>Department</th>
                  </tr>
              </thead>
              


                  {spitTable}

              

          </table>
          </div>


      </div>

    )
  }
});



module.exports = SearchPage;