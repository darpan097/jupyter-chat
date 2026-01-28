/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */

// import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import FeedbackIcon from '@mui/icons-material/Feedback';
import { Box, IconButton, Tooltip } from '@mui/material';
import React, { useState } from 'react';
import { FeedbackDialog } from './feedback-dialog';
import { IChatModel } from '../../model';

const TOOLBAR_CLASS = 'jp-chat-toolbar';

/**
 * The toolbar attached to a message.
 */
export function MessageToolbar(props: MessageToolbar.IProps): JSX.Element {
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const buttons: JSX.Element[] = [];

  // if (props.edit !== undefined) {
  //   const editButton = (
  //     <Tooltip key="edit" title="Edit" placement="top" arrow>
  //       <span>
  //         <IconButton
  //           onClick={props.edit}
  //           aria-label="Edit"
  //           sx={{
  //             width: '24px',
  //             height: '24px',
  //             padding: 0,
  //             lineHeight: 0
  //           }}
  //         >
  //           <EditIcon sx={{ fontSize: '16px' }} />
  //         </IconButton>
  //       </span>
  //     </Tooltip>
  //   );
  //   buttons.push(editButton);
  // }

  if (props.isBot) {
    const feedbackButton = (
      <Tooltip key="feedback" title="Give feedback" placement="top" arrow>
        <span>
          <IconButton
            onClick={() => setFeedbackOpen(true)}
            aria-label="Give feedback"
            sx={{
              width: '24px',
              height: '24px',
              padding: 0,
              lineHeight: 0
            }}
          >
            <FeedbackIcon sx={{ fontSize: '16px' }} />
          </IconButton>
        </span>
      </Tooltip>
    );
    buttons.push(feedbackButton);
  }

  if (props.delete !== undefined) {
    const deleteButton = (
      <Tooltip key="delete" title="Delete" placement="top" arrow>
        <span>
          <IconButton
            onClick={props.delete}
            aria-label="Delete"
            sx={{
              width: '24px',
              height: '24px',
              padding: 0,
              lineHeight: 0
            }}
          >
            <DeleteIcon sx={{ fontSize: '16px' }} />
          </IconButton>
        </span>
      </Tooltip>
    );
    buttons.push(deleteButton);
  }

  return (
    <>
      <Box
        className={`${TOOLBAR_CLASS} ${props.isBot ? 'jp-chat-toolbar-bot' : 'jp-chat-toolbar-user'}`}
        sx={{
          display: 'flex',
          gap: 2,
          justifyContent: 'flex-end'
        }}
      >
        {buttons}
      </Box>
      {props.isBot && (
        <FeedbackDialog
          open={feedbackOpen}
          onClose={() => setFeedbackOpen(false)}
          messageBody={props.messageBody}
          model={props.model}
          messageIndex={props.messageIndex}
        />
      )}
    </>
  );
}

export namespace MessageToolbar {
  export interface IProps {
    edit?: () => void;
    delete?: () => void;
    isBot?: boolean;
    messageBody?: string;
    model?: IChatModel;
    messageIndex?: number;
  }
}
