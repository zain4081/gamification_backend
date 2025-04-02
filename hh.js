import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

// ** Custom Components
import Avatar from '@components/avatar'

import axiosInstance from "@src/interceptor/axios";
// ** Blank Avatar Image
import blankAvatar from '@src/assets/images/avatars/avatar-blank.png'
// ** Third Party Components
import classnames from 'classnames'
import { ReactSortable } from 'react-sortablejs'
import PerfectScrollbar from 'react-perfect-scrollbar'
import { Menu, MoreVertical } from 'react-feather'

// ** Reactstrap Imports
import {
  Input,
  Badge,
  DropdownMenu,
  DropdownItem,
  DropdownToggle,
  UncontrolledDropdown,
  Button
} from 'reactstrap'

const Requirements = props => {
  const { projectIdSetter, refreshpage, projectStatusSetter } = props;
  const [ refetch, setRefetch] = useState(true);
  const [projectId, setProjectId] = useState();
  const [projects, setProjects] = useState([]);
  const [requirements, setRequirements] = useState([]);
  const [voteValues, setVoteValues] = useState({}); // Track vote value for each requirement

  // Fetch projects on initial load
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await axiosInstance.get('/project/list/', { params: { p: 1 } });
        setProjects(response.data.results);
        if (!projectId && response.data.results.length > 0) {
          let firstProject = response.data.results[0];
          setProjectId(firstProject.id);
          projectIdSetter(firstProject.id);
          projectStatusSetter(firstProject.voting_status);
        }
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    }
    fetchProjects();
  }, []);

  // Fetch requirements for the selected project
  useEffect(() => {
    if (!projectId) return;
    const fetchRequirements = async () => {
      try {
        const response = await axiosInstance.get(`/project/${projectId}/requirements/`);
        setRequirements(response.data);
      } catch (error) {
        console.error('Error fetching requirements:', error);
      }
    }
    fetchRequirements();
  }, [projectId, refreshpage, refetch]);

  // Submit vote with points
  const submitVote = async (requirement_id, data) => {
    try {
      const response = await axiosInstance.post(`/project/giveVote/${requirement_id}/`, data);
      console.log("Vote submitted:", response);
    } catch (error) {
      console.error('Error submitting vote:', error);
    }
  }

  // Handle project selection change
  const handleProjectChange = e => {
    setProjectId(e.target.value);
    projectStatusSetter(e.target.options[e.target.selectedIndex].getAttribute('data-status'));
    projectIdSetter(e.target.value);
  };

  // Render tags for requirements
  const renderTags = arr => {
    const badgeColor = {
      team: 'light-primary',
      low: 'light-success',
      medium: 'light-warning',
      high: 'light-danger',
      update: 'light-info'
    };

    return arr.map(item => (
      <Badge className='text-capitalize' key={item} color={badgeColor[item]} pill>
        {item}
      </Badge>
    ));
  };

  // Render avatar for assignees
  const renderAvatar = obj => {
    const item = obj.assignee;
    return item.avatar ? (
      <Avatar img={item.avatar} imgHeight='32' imgWidth='32' />
    ) : (
      <Avatar img={blankAvatar} imgHeight='32' imgWidth='32' />
    );
  };

  // Handle voting on a requirement
  const handleVote = async (item, value) => {
    const data = {
      points: value
    };
    await submitVote(item.id, data); // Submit the vote with requirement_id and data
    setRefetch(!refetch);
  };

  // Handle vote value change for a specific requirement
  const handleVoteChange = (requirementId, value) => {
    setVoteValues(prevState => ({
      ...prevState,
      [requirementId]: value
    }));
  };

  const handleMarkRequirement = async (requirementId, isMarked) => {
    try {
      const response = await axiosInstance.post(`/project/requirement/${requirementId}/mark/`, { is_marked: isMarked });
      console.log("Requirement marked:", response);
      setRefetch(!refetch);
    } catch (error) {
      console.error('Error marking requirement:', error);
    }
  };

  // Render the list of requirements
  const renderRequirements = () => {
    return (
      <PerfectScrollbar className='list-group todo-task-list-wrapper' options={{ wheelPropagation: false }}>
        {requirements.length ? (
          <ReactSortable tag='ul' list={requirements} handle='.drag-icon' className='todo-task-list media-list' setList={newState => console.log('Reordered', newState)}>
            {requirements.map((item, index) => (
              <li key={`${item.id}-${index}`} className={classnames('todo-item', { completed: item.isCompleted })}>
                <div className='todo-title-wrapper'>
                  <div className='todo-title-area'>
                    <MoreVertical className='drag-icon' />
                    <div className='form-check'>
                      <Input type='checkbox' id={item.name} checked={item.isCompleted} onChange={() => console.log('Update completion:', item.name)} />
                    </div>
                    <span className='todo-title'>{item.name}</span>
                  </div>
                  <div className='todo-item-action mt-lg-0 mt-50'>
                    {item.tags && item.tags.length ? (
                      <div className='badge-wrapper me-1'>{renderTags(item.tags)}</div>
                    ) : null}
                    {item.dueDate ? (
                      <small className='text-nowrap text-muted me-1'>
                        {new Date(item.dueDate).toLocaleString('default', { month: 'short' })}{' '}
                        {new Date(item.dueDate).getDate().toString().padStart(2, '0')}
                      </small>
                    ) : null}
                    {item.assignee ? renderAvatar(item) : null}
                    {item.score !== undefined && (
                      <Badge color='light-primary' className='ms-1'>Score: {item.score}</Badge>
                    )}
                    {item.users_status && (
                      <Badge color='light-secondary' className='ms-1'>Votes: {item.users_status.voted}/{item.users_status.all}</Badge>
                    )}
                    {item.is_all_users_voted && (
                      <Badge color='light-success' className='ms-1'>Voting Completed</Badge>
                    )}
                    {/* New Conditional Rendering Logic */}
                    {typeof item.is_marked !== 'undefined' && (
                      <div className='ms-2'>
                        {item.is_marked ? (
                          item.is_confirmed ? (
                            <span title="Confirmed">
                              🔒 {/* Lock Icon */}
                            </span>
                          ) : (
                            <Badge color='light-danger'>Marked as No</Badge>
                          )
                        ) : (
                          <div className='mark-form'>
                            <label>Mark as:</label>
                            <Button color='success' size='sm' className='ms-1' onClick={() => handleMarkRequirement(item.id, true)}>Yes</Button>
                            <Button color='danger' size='sm' className='ms-1' onClick={() => handleMarkRequirement(item.id, false)}>No</Button>
                          </div>
                        )}
                      </div>
                    )}
                    {typeof item.has_voted !== 'undefined' && !item.has_voted && (
                      <div className='vote-section ms-1'>
                        <label htmlFor={`vote-${item.id}`}>Vote:</label>
                        <Input
                          id={`vote-${item.id}`}
                          type='select'
                          value={voteValues[item.id] || item.min_points} // Default value set to min_points
                          onChange={e => handleVoteChange(item.id, e.target.value)} // Handle input change for specific requirement
                        >
                          {Array.from({ length: item.max_points - item.min_points + 1 }, (_, index) => (
                            <option key={index} value={item.min_points + index}>
                              {item.min_points + index}
                            </option>
                          ))}
                        </Input>
                        <Button color='primary' className='ms-1' onClick={() => handleVote(item, voteValues[item.id] || item.min_points)}>Submit</Button>
                      </div>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ReactSortable>
        ) : (
          <div className='no-results show'>
            <h5>No Items Found</h5>
          </div>
        )}
      </PerfectScrollbar>
    );
  };

  return (
    <div className='todo-app-list'>
      <div className='my-2'>
        <label htmlFor='project-select' className='form-label'>Select Project</label>
        <select id='project-select' className='form-select' value={projectId} onChange={handleProjectChange}>
          {projects && projects.length > 0 && projects.map(project => (
            <option key={project.id} value={project.id} data-status={project.voting_status}>{project.name}</option>
          ))}
        </select>
      </div>
      {renderRequirements()}
    </div>
  );
};

export default Requirements;
